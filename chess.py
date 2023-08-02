
import pygame
import sys


# pygame setup
pygame.init()
screen_width = 1080
screen_height = 720
screen = pygame.display.set_mode((1080, 720))
pygame.display.set_caption('Chess')
clock = pygame.time.Clock()

player1_timer = 300000  # 5 minutes
player2_timer = 300000  # 5 minutes
timer_active = 1  # The timer currently active: None, 1, or 2


class Piece:
    def __init__(self, type, color, location, state, image, small):
        self.type = type
        self.color = color
        self.location = location
        self.state = state
        self.image = image
        self.small = small
        self.dragging = False
        self.start = None
        self.end = None
        self.moved = False
        self.is_promo_piece = False
        
    
    def draw(self):
        screen.blit(self.image, self.rect.topleft)

    def move(self, location, square):
        self.location = location
        # square.occupied_piece = self

class Square:
    def __init__(self, x_coord, y_coord, occupied_piece, number):
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.coord = (x_coord, y_coord)
        self.occupied_piece = occupied_piece
        self.number = number


active_piece = None
def main():
    game_state = 'white_selection'
    selected_piece = None
    selected_square = None
    checking_l = False
    checking_r = False
    passant_l = False
    passant_r = False
    check = False
    run = True
    checkmate = False
    step = 0
    pawn_promo_square = False
    temp_white_pieces = []
    temp_black_pieces = []
    while run:
        clock.tick(60)
        screen.fill('light gray')
        draw_board(pawn_promo_square)
        draw_pieces()
        check = check_check(game_state)
        draw_options(selected_piece, passant_l, passant_r, check)
        checkmate = check_mate(game_state, passant_l, passant_r)
        draw_timers() 
        draw_captured_pieces()
        for event in pygame.event.get():
            # quit the game
            if event.type == pygame.QUIT:
                run = False
            #region move white pieces
            if game_state == 'white_selection':
                counter = 0
                for piece in white_pieces:
                    check = check_check('white_selection')
                    if piece.type == 'pawn':
                        checking_l = str(piece.location-17) + ',' + str(piece.location-1)
                        checking_r = str(piece.location-15) + ',' + str(piece.location+1)
                        if step != 0:
                            if moves[step-1] == checking_l:
                                options = check_option(piece, True, False, check)
                                passant_l = True
                            elif moves[step-1] == checking_r:
                                options = check_option(piece, False, True, check)
                                passant_r = True
                            else:
                                options = check_option(piece, False, False, check)
                        else:
                            options = check_option(piece, False, False, check)
                    else:
                        options = check_option(piece, False, False, check)
                    options = check_check_check(options, piece)
                    if options:
                        counter += 1

                if counter == 0:
                    if check == True:
                        game_state = 'black_wins'
                    else:
                        game_state = 'stalemate'
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x_coord_click = event.pos[0] // 90
                    y_coord_click = event.pos[1] // 90
                    click_coords = (x_coord_click, y_coord_click)
                    passant_r = False
                    passant_l = False
                    checking_l = False
                    checking_r = False
                    for index, square in enumerate(sq):
                        if sq[index].coord == click_coords and sq[index].occupied_piece != None and sq[index].occupied_piece.color == 'white':
                            selected_square = index
                            selected_piece = sq[selected_square].occupied_piece
                            selected_piece.start = sq[selected_square]
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if selected_piece:
                        checking_l = str(selected_piece.location-17) + ',' + str(selected_piece.location-1)
                        checking_r = str(selected_piece.location-15) + ',' + str(selected_piece.location+1)
                        check = check_check(game_state)
                        if step != 0:
                            if moves[step-1] == checking_l:
                                options = check_option(selected_piece, True, False, check)
                                passant_l = True
                            elif moves[step-1] == checking_r:
                                options = check_option(selected_piece, False, True, check)
                                passant_r = True
                            else:
                                options = check_option(selected_piece, False, False, check)
                        else:
                            options = check_option(selected_piece, False, False, check)
                        options = check_check_check(options, selected_piece)
                        x_coord_click = event.pos[0] // 90
                        y_coord_click = event.pos[1] // 90
                        click_location = x_coord_click + y_coord_click*8
                        selected_piece.end = sq[click_location]
                        if selected_piece.end != None and selected_piece.end != selected_piece.start and click_location in options:
                            selected_piece.move(click_location, sq[click_location])
                            selected_piece.start.occupied_piece = None
                            selected_piece.end = sq[click_location]
                            # castling
                            if selected_piece.type == 'king' and click_location == selected_piece.start.number+2:
                                white_rook_h.move(click_location-1, sq[click_location-1])
                                sq[click_location-1].occupied_piece = white_rook_h
                            if selected_piece.type == 'king' and click_location == selected_piece.start.number-2:
                                white_rook_a.move(click_location+1, sq[click_location+1])
                                sq[click_location+1].occupied_piece = white_rook_a
                            if sq[click_location].occupied_piece != None and sq[click_location].occupied_piece.color is 'black':
                                black_piece = sq[click_location].occupied_piece
                                white_captured_pieces.append(black_piece)
                                black_pieces.remove(black_piece)
                            if click_location == selected_piece.start.number + 9 or click_location == selected_piece.start.number + 7:
                                if passant_l is True and selected_piece.type == 'pawn' and sq[click_location+8].occupied_piece.type == 'pawn' and sq[click_location+8].occupied_piece.color == 'black':
                                    black_piece = sq[click_location+8].occupied_piece
                                    white_captured_pieces.append(black_piece)
                                    sq[black_piece.location].occupied_piece = None
                                    black_pieces.remove(black_piece)
                                if passant_r is True and selected_piece.type == 'pawn' and sq[click_location+8].occupied_piece.type == 'pawn' and sq[click_location+8].occupied_piece.color == 'black':
                                    black_piece = sq[click_location+8].occupied_piece
                                    white_captured_pieces.append(black_piece)
                                    sq[black_piece.location].occupied_piece = None
                                    black_pieces.remove(black_piece)
                            selected_piece.end.occupied_piece = selected_piece
                            moves.append(str(selected_piece.start.number) + "," + str(click_location))
                            step += 1
                            selected_piece.end = None
                            selected_piece.start = None
                            selected_piece.moved = True
                            checking_r = False
                            checking_l = False
                            passant_r = False
                            passant_l = False
                            check = False
                            if click_location in pawn_promotion_squares and selected_piece.type == 'pawn':
                                game_state = 'white_pawn_promo'
                            else:
                                selected_piece = None
                                game_state = 'black_selection'
                                switch_timer()
                #endregion
            #region black move
            if game_state == 'black_selection':
                counter = 0
                for piece in black_pieces:
                    check = check_check('black_selection')
                    if piece.type == 'pawn':
                        checking_l = str(piece.location-17) + ',' + str(piece.location-1)
                        checking_r = str(piece.location-15) + ',' + str(piece.location+1)
                        if step != 0:
                            if moves[step-1] == checking_l:
                                options = check_option(piece, True, False, check)
                                passant_l = True
                            elif moves[step-1] == checking_r:
                                options = check_option(piece, False, True, check)
                                passant_r = True
                            else:
                                options = check_option(piece, False, False, check)
                        else:
                            options = check_option(piece, False, False, check)
                    else:
                        options = check_option(piece, False, False, check)
                    options = check_check_check(options, piece)
                    if options:
                        counter += 1
                if counter == 0:
                    if check == True:
                        game_state = 'white_wins'
                    else:
                        game_state = 'stalemate'
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x_coord_click = event.pos[0] // 90
                    y_coord_click = event.pos[1] // 90
                    passant_r = False
                    passant_l = False
                    checking_l = False
                    checking_r = False
                    click_coords = (x_coord_click, y_coord_click)
                    for index, square in enumerate(sq):
                        if sq[index].coord == click_coords and sq[index].occupied_piece != None and sq[index].occupied_piece.color == 'black':
                            selected_square = index
                            selected_piece = sq[selected_square].occupied_piece
                            selected_piece.start = sq[selected_square]
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if selected_piece:
                        checking_l = str(selected_piece.location+15) + ',' + str(selected_piece.location-1)
                        checking_r = str(selected_piece.location+17) + ',' + str(selected_piece.location+1)
                        check = check_check(game_state)
                        if step != 0:
                            if moves[step-1] == checking_l:
                                options = check_option(selected_piece, True, False, check)
                                passant_l = True
                            elif moves[step-1] == checking_r:
                                options = check_option(selected_piece, False, True, check)
                                passant_r = True
                            else:
                                options = check_option(selected_piece, False, False, check)
                        else:
                            options = check_option(selected_piece, False, False, check)
                        options = check_check_check(options, selected_piece)
                        x_coord_click = event.pos[0] // 90
                        y_coord_click = event.pos[1] // 90
                        click_location = x_coord_click + y_coord_click*8
                        selected_piece.end = sq[click_location]
                        if selected_piece.end != None and selected_piece.end != selected_piece.start and click_location in options:
                            selected_piece.move(click_location, sq[click_location])
                            selected_piece.start.occupied_piece = None
                            selected_piece.end = sq[click_location]
                            # castling
                            if selected_piece.type == 'king' and click_location == selected_piece.start.number+2:
                                black_rook_h.move(click_location-1, sq[click_location-1])
                                sq[click_location-1].occupied_piece = black_rook_h
                            if selected_piece.type == 'king' and click_location == selected_piece.start.number-2:
                                black_rook_a.move(click_location+1, sq[click_location+1])
                                sq[click_location+1].occupied_piece = black_rook_h
                            if sq[click_location].occupied_piece != None and sq[click_location].occupied_piece.color is 'white':
                                white_piece = sq[click_location].occupied_piece
                                black_captured_pieces.append(white_piece)
                                white_pieces.remove(white_piece)
                            if click_location == selected_piece.start.number + 9 or click_location == selected_piece.start.number + 7:
                                if passant_l is True and selected_piece.type == 'pawn' and sq[click_location-8].occupied_piece.type == 'pawn' and sq[click_location-8].occupied_piece.color == 'white':
                                    white_piece = sq[click_location-8].occupied_piece
                                    black_captured_pieces.append(white_piece)
                                    sq[white_piece.location].occupied_piece = None
                                    white_pieces.remove(white_piece)
                                if passant_r is True and selected_piece.type == 'pawn' and sq[click_location-8].occupied_piece.type == 'pawn' and sq[click_location-8].occupied_piece.color == 'white':
                                    white_piece = sq[click_location-8].occupied_piece
                                    black_captured_pieces.append(white_piece)
                                    sq[white_piece.location].occupied_piece = None
                                    white_pieces.remove(white_piece)
                            selected_piece.end.occupied_piece = selected_piece
                            moves.append(str(selected_piece.start.number) + "," + str(click_location))
                            step += 1
                            selected_piece.end = None
                            selected_piece.start = None
                            selected_piece.moved = True
                            checking_l = False
                            checking_r = False
                            passant_l = False
                            passant_r = False
                            check = False
                            if click_location in pawn_promotion_squares and selected_piece.type == 'pawn':
                                game_state = 'black_pawn_promo'
                            else:
                                selected_piece = None
                                game_state = 'white_selection'
                                switch_timer()
            
            #endregion
            
            if game_state == 'white_pawn_promo':
                pawn_promo_square = selected_piece.location
                temp_promo_squares = [pawn_promo_square, pawn_promo_square+8, pawn_promo_square+16, pawn_promo_square+24]
                initial_board_state = [sq[i].occupied_piece for i in range(64)]
                def restore_board_state():
                    for i in range(64):
                        sq[i].occupied_piece = initial_board_state[i]
                for square in temp_promo_squares:
                    if sq[square].occupied_piece is not None:
                        if sq[square].occupied_piece.color == 'white':
                            try:
                                if sq[square].occupied_piece.is_promo_piece == False:
                                    temp_white_pieces.append(sq[square].occupied_piece)
                                white_pieces.remove(sq[square].occupied_piece)
                            except ValueError:
                                pass  # The piece is not in white_pieces, ignore the error
                        elif sq[square].occupied_piece.color == 'black':
                            try: 
                                temp_black_pieces.append(sq[square].occupied_piece)
                                black_pieces.remove(sq[square].occupied_piece)
                            except ValueError:
                                pass  # The piece is not in black_pieces, ignore the error
                    sq[square].occupied_piece = None               
                white_queen_temp = Piece('queen', 'white', pawn_promo_square, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-queen.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-queen.png'), (45, 45)))
                white_queen_temp.is_promo_piece = True
                white_knight_temp = Piece('knight', 'white', pawn_promo_square+8, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-knight.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-knight.png'), (45, 45)))
                white_knight_temp.is_promo_piece = True
                white_rook_temp = Piece('rook', 'white', pawn_promo_square+16, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-rook.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-rook.png'), (45, 45)))
                white_rook_temp.is_promo_piece = True
                white_bishop_temp = Piece('bishop', 'white', pawn_promo_square+24, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-bishop.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-bishop.png'), (45, 45)))
                white_bishop_temp.is_promo_piece = True
                temp_pieces = [white_queen_temp, white_knight_temp, white_rook_temp, white_bishop_temp]
                for piece in temp_pieces:
                    white_pieces.append(piece)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x_coord_click = event.pos[0] // 90
                    y_coord_click = event.pos[1] // 90
                    click_location = x_coord_click + y_coord_click*8
                    if click_location in temp_promo_squares:
                        if click_location == pawn_promo_square:
                            new_piece = white_queen_temp
                        elif click_location == pawn_promo_square+8:
                            new_piece = white_knight_temp
                        elif click_location == pawn_promo_square+16:
                            new_piece = white_rook_temp
                        elif click_location == pawn_promo_square+24:
                            new_piece = white_bishop_temp
                        
                        # Remove temporary promotion pieces from white_pieces
                        for piece in white_pieces[:]:
                            if piece.is_promo_piece:
                                white_pieces.remove(piece)

                        # Add back the pieces that were originally on the squares
                        for piece in temp_white_pieces:
                            white_pieces.append(piece)
        
                        for piece in temp_black_pieces:
                            if piece.location is not selected_piece.location:
                                black_pieces.append(piece)
                        # Add the new promoted piece to white_pieces
                        white_pieces.append(new_piece)

                        # Update the location of the promoted piece
                        new_piece.location = pawn_promo_square
                        new_piece.is_promo_piece = False
                        # Remove the original pawn from white_pieces
                        white_pieces.remove(selected_piece)

                        # Set the square of the pawn to the new promoted piece
                        sq[pawn_promo_square].occupied_piece = new_piece

                        pawn_promo_square = False
                        restore_board_state()  # Corrected the function call with parentheses
                        
                        selected_piece = None
                        temp_black_pieces = []
                        temp_white_pieces = []

                        game_state = 'black_selection'
                        switch_timer()

            if game_state == 'black_pawn_promo':
                pawn_promo_square = selected_piece.location
                temp_promo_squares = [pawn_promo_square, pawn_promo_square-8, pawn_promo_square-16, pawn_promo_square-24]
                initial_board_state = [sq[i].occupied_piece for i in range(64)]
                def restore_board_state():
                    for i in range(64):
                        sq[i].occupied_piece = initial_board_state[i]
                for square in temp_promo_squares:
                    if sq[square].occupied_piece is not None:
                        if sq[square].occupied_piece.color == 'black':
                            try:
                                if sq[square].occupied_piece.is_promo_piece == False:
                                    temp_black_pieces.append(sq[square].occupied_piece)
                                black_pieces.remove(sq[square].occupied_piece)
                            except ValueError:
                                pass  # The piece is not in white_pieces, ignore the error
                        elif sq[square].occupied_piece.color == 'white':
                            try: 
                                temp_white_pieces.append(sq[square].occupied_piece)
                                white_pieces.remove(sq[square].occupied_piece)
                            except ValueError:
                                pass  # The piece is not in black_pieces, ignore the error
                    sq[square].occupied_piece = None              
                black_queen_temp = Piece('queen', 'black', pawn_promo_square, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-queen.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-queen.png'), (45, 45)))
                black_queen_temp.is_promo_piece = True
                black_knight_temp = Piece('knight', 'black', pawn_promo_square-8, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-knight.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-knight.png'), (45, 45)))
                black_knight_temp.is_promo_piece = True
                black_rook_temp = Piece('rook', 'black', pawn_promo_square-16, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-rook.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-rook.png'), (45, 45)))
                black_rook_temp.is_promo_piece = True
                black_bishop_temp = Piece('bishop', 'black', pawn_promo_square-24, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-bishop.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-bishop.png'), (45, 45)))
                black_bishop_temp.is_promo_piece = True
                temp_pieces = [black_queen_temp, black_knight_temp, black_rook_temp, black_bishop_temp]
                for piece in temp_pieces:
                    black_pieces.append(piece)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x_coord_click = event.pos[0] // 90
                    y_coord_click = event.pos[1] // 90
                    click_location = x_coord_click + y_coord_click*8
                    if click_location in temp_promo_squares:
                        if click_location == pawn_promo_square:
                            new_piece = black_queen_temp
                        elif click_location == pawn_promo_square+8:
                            new_piece = black_knight_temp
                        elif click_location == pawn_promo_square+16:
                            new_piece = black_rook_temp
                        elif click_location == pawn_promo_square+24:
                            new_piece = black_bishop_temp
                        
                        # Remove temporary promotion pieces from white_pieces
                        for piece in black_pieces[:]:
                            if piece.is_promo_piece:
                                black_pieces.remove(piece)

                        # Add back the pieces that were originally on the squares
                        for piece in temp_black_pieces:
                            black_pieces.append(piece)
        
                        for piece in temp_white_pieces:
                            if piece.location is not selected_piece.location:
                                white_pieces.append(piece)
                        # Add the new promoted piece to white_pieces
                        black_pieces.append(new_piece)

                        # Update the location of the promoted piece
                        new_piece.location = pawn_promo_square
                        new_piece.is_promo_piece = False
                        # Remove the original pawn from white_pieces
                        black_pieces.remove(selected_piece)

                        # Set the square of the pawn to the new promoted piece
                        sq[pawn_promo_square].occupied_piece = new_piece

                        pawn_promo_square = False
                        restore_board_state()  # Corrected the function call with parentheses
                        
                        selected_piece = None
                        temp_black_pieces = []
                        temp_white_pieces = []

                        game_state = 'white_selection'
                        switch_timer()
            if game_state == 'white_wins':
                display_result("White wins!")
            if game_state == 'black_wins':
                display_result("Black wins!")
            if game_state == 'stalemate':
                display_result("Stalemate")
        update_timer()
        pygame.display.flip()
    pygame.quit()

sq = []
sq_left_edge = [0, 8, 16, 24, 32, 40, 48, 56]
sq_right_edge = [7, 15, 23, 31, 39, 47, 55, 63]
sq_bottom_edge = [56, 57, 58, 59, 60, 61, 62, 63]
sq_top_edge = [0, 1, 2, 3, 4, 5, 6, 7]
pawn_promotion_squares = sq_top_edge + sq_bottom_edge


def draw_board(pawn_promo_square = False):
    counter = 0
    temp_promo_squares = []
    if pawn_promo_square is not False:
        if pawn_promo_square in sq_top_edge:
            temp_promo_squares = [pawn_promo_square, pawn_promo_square+8, pawn_promo_square+16, pawn_promo_square+24]
        elif pawn_promo_square in sq_bottom_edge:
            temp_promo_squares = [pawn_promo_square, pawn_promo_square-8, pawn_promo_square-16, pawn_promo_square-24]
    for row in range(8):
        for column in range(8):
            sq.append(Square(column, row, None, counter))
            if counter in temp_promo_squares:
                pygame.draw.rect(screen, '#ffffff', [column*90, row*90, 90, 90])  # Swap row and column here
            elif row % 2 == 0 and column % 2 != 0:
                pygame.draw.rect(screen, '#b58863', [column*90, row*90, 90, 90])  # Swap row and column here
            elif row % 2 != 0 and column % 2 == 0:
                pygame.draw.rect(screen, '#b58863', [column*90, row*90, 90, 90])  # Swap row and column here
            elif row % 2 == 0 and column % 2 == 0:
                pygame.draw.rect(screen, '#f0d9b5', [column*90, row*90, 90, 90])  # Swap row and column here
            elif row % 2 != 0 and column % 2 != 0:
                pygame.draw.rect(screen, '#f0d9b5', [column*90, row*90, 90, 90])  # Swap row and column here
            counter += 1


#region initialize pieces in white_pieces and black_pieces
white_rook_a = Piece('rook', 'white', 56, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-rook.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-rook.png'), (45, 45)))
white_knight_b = Piece('knight', 'white', 57, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-knight.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-knight.png'), (45, 45)))
white_bishop_c = Piece('bishop', 'white', 58, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-bishop.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-bishop.png'), (45, 45)))
white_queen_d = Piece('queen', 'white', 59, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-queen.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-queen.png'), (45, 45)))
white_king_e = Piece('king', 'white', 60, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-king.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-king.png'), (45, 45)))
white_bishop_f = Piece('bishop', 'white', 61, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-bishop.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-bishop.png'), (45, 45)))
white_knight_g = Piece('knight', 'white', 62, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-knight.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-knight.png'), (45, 45)))
white_rook_h = Piece('rook', 'white', 63, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-rook.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-rook.png'), (45, 45)))

white_pawn_a = Piece('pawn', 'white', 48, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (45, 45)))
white_pawn_b = Piece('pawn', 'white', 49, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (45, 45)))
white_pawn_c = Piece('pawn', 'white', 50, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (45, 45)))
white_pawn_d = Piece('pawn', 'white', 51, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (45, 45)))
white_pawn_e = Piece('pawn', 'white', 52, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (45, 45)))
white_pawn_f = Piece('pawn', 'white', 53, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (45, 45)))
white_pawn_g = Piece('pawn', 'white', 54, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (45, 45)))
white_pawn_h = Piece('pawn', 'white', 55, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/white-pawn.png'), (45, 45)))

white_pieces = [white_rook_a, white_pawn_a, white_knight_b, white_bishop_c, white_queen_d, white_king_e, white_knight_g, white_bishop_f, white_rook_h, white_pawn_b, white_pawn_c, white_pawn_d, white_pawn_e, white_pawn_f, white_pawn_h, white_pawn_g]
white_captured_pieces = []

black_rook_a = Piece('rook', 'black', 0, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-rook.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-rook.png'), (45, 45)))
black_knight_b = Piece('knight', 'black', 1, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-knight.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-knight.png'), (45, 45)))
black_bishop_c = Piece('bishop', 'black', 2, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-bishop.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-bishop.png'), (45, 45)))
black_queen_d = Piece('queen', 'black', 3, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-queen.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-queen.png'), (45, 45)))
black_king_e = Piece('king', 'black', 4, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-king.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-king.png'), (45, 45)))
black_bishop_f = Piece('bishop', 'black', 5, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-bishop.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-bishop.png'), (45, 45)))
black_knight_g = Piece('knight', 'black', 6, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-knight.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-knight.png'), (45, 45)))
black_rook_h = Piece('rook', 'black', 7, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-rook.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-rook.png'), (45, 45)))


black_pawn_a = Piece('pawn', 'black', 8, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (45, 45)))
black_pawn_b = Piece('pawn', 'black', 9, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (45, 45)))
black_pawn_c = Piece('pawn', 'black', 10, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (45, 45)))
black_pawn_d = Piece('pawn', 'black', 11, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (45, 45)))
black_pawn_e = Piece('pawn', 'black', 12, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (45, 45)))
black_pawn_f = Piece('pawn', 'black', 13, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (45, 45)))
black_pawn_g = Piece('pawn', 'black', 14, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (45, 45)))
black_pawn_h = Piece('pawn', 'black', 15, 'active', pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (90, 90)), pygame.transform.scale(pygame.image.load('chess/assets/pieces/black-pawn.png'), (45, 45)))


black_pieces = [black_rook_a, black_pawn_a, black_knight_b, black_bishop_c, black_queen_d, black_king_e, black_knight_g, black_bishop_f, black_rook_h, black_pawn_b, black_pawn_c, black_pawn_d, black_pawn_e, black_pawn_f, black_pawn_h, black_pawn_g]
black_captured_pieces = []

moves=[]
turn=1
step = 0
#endregion

def draw_pieces():
    for piece in white_pieces:
        screen.blit(piece.image, ((sq[piece.location].x_coord*90), (sq[piece.location].y_coord)*90))
        sq[piece.location].occupied_piece = piece 
    for piece in black_pieces:
        screen.blit(piece.image, ((sq[piece.location].x_coord*90), (sq[piece.location].y_coord)*90))
        sq[piece.location].occupied_piece = piece
        
    
def check_option(checking_piece, passant_l, passant_r, check, check2=False):
    type = checking_piece.type
    square = checking_piece.location
    color = checking_piece.color
    if color == 'black':
        state = 'black_selection'
        opponent_pieces = white_pieces
    else:
        state = 'white_selection'
        opponent_pieces = black_pieces
    valid = []
    initial_board_state = [sq[i].occupied_piece for i in range(64)]

    # Restoring the board state after checking each move
    def restore_board_state():
        for i in range(64):
            sq[i].occupied_piece = initial_board_state[i]

    # Restoring the board state after each iteration
    def restore_iteration_state():
        checking_piece.location = square

    # Restoring the board state after each move
    def restore_move_state():
        for move in valid:
            sq[move].occupied_piece = None
    # white pawn
    if check is False:
        if type == 'pawn' and color=='white':
            #move up one
            if sq[square-8].occupied_piece is None:
                valid.append(square-8)
            #move double
            if checking_piece.moved is False and sq[square-8].occupied_piece is None and sq[square-16].occupied_piece is None:
                valid.append(square-16)
            #capture right
            if sq[square-7].occupied_piece is not None and square not in sq_right_edge:
                if sq[square-7].occupied_piece.color == 'black':
                    valid.append(square-7)
            if sq[square-9].occupied_piece is not None and square not in sq_left_edge:
                if sq[square-9]. occupied_piece.color == 'black':
                    valid.append(square-9)
            if passant_l is True:
                valid.append(square-9)
            if passant_r is True:
                valid.append(square-7)
        if type == 'king':
            potential_moves = [square + 1, square - 1, square - 9, square - 8, square - 7, square + 7, square + 8, square + 9, square + 2, square - 2]
            valid = [move for move in potential_moves if 0 <= move < 64 and (sq[move].occupied_piece is None or sq[move].occupied_piece.color != color)]
            if square in sq_left_edge:
                rm = [square-1, square-9, square+7]
                valid = [x for x in valid if x not in rm]
            if square in sq_right_edge:
                rm = [square+1, square-7, square+9]
                valid = [x for x in valid if x not in rm]
            if square in sq_top_edge:
                rm = [square-7, square-8, square-9]
                valid = [x for x in valid if x not in rm]
            if square in sq_bottom_edge:
                rm = [square+7, square+8, square+9]
                valid = [x for x in valid if x not in rm]
            if sq[square+3].occupied_piece is None:
                rm = [square+2]
                valid = [x for x in valid if x not in rm]
            if sq[square+3].occupied_piece is not None:
                if checking_piece.moved == True or sq[square+3].occupied_piece.type is not 'rook' or sq[square+3].occupied_piece.color is not color or sq[square+3].occupied_piece.moved is True or sq[square+1].occupied_piece is not None or sq[square+2].occupied_piece is not None or check2 == True:
                    rm = [square+2]
                    valid = [x for x in valid if x not in rm]
            if sq[square-4].occupied_piece is None:
                rm = [square-2]
                valid = [x for x in valid if x not in rm]
            if sq[square-4].occupied_piece is not None:
                if checking_piece.moved == True or sq[square-4].occupied_piece.type is not 'rook' or sq[square-4].occupied_piece.color is not color or sq[square-4].occupied_piece.moved is True or sq[square-1].occupied_piece is not None or sq[square-2].occupied_piece is not None or sq[square-3].occupied_piece is not None or check2 == True:
                    rm = [square-2]
                    valid = [x for x in valid if x not in rm]
        if type == 'queen':
            #region horizantally
            # up
            for i in range(square-8, -1, -8):
                if i+8 in sq_top_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece is not None and sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                valid.append(i)
            # down
            for i in range(square+8, 64, 8):
                if i-8 in sq_bottom_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                valid.append(i)
            #right
            for i in range(square+1, 64, 1):
                if i-1 in sq_right_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                if i in sq_right_edge:
                    valid.append(i)
                    break
                valid.append(i)
                    
            #left
            for i in range(square-1, -1, -1):
                if i+1 in sq_left_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                if i in sq_left_edge:
                    valid.append(i)
                    break
                valid.append(i)
            #endregion
            
            #region diagonally
            # up right
            for i in range(square-7, -1, -7):
                if i+7 in sq_top_edge or i+7 in sq_right_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece is not None and sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                if i in sq_right_edge or i in sq_top_edge:
                    valid.append(i)
                    break
                valid.append(i)

            # up left
            for i in range(square-9, -1, -9):
                if i+9 in sq_top_edge or i+9 in sq_left_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece is not None and sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                if i in sq_left_edge or i in sq_top_edge:
                    valid.append(i)
                    break
                valid.append(i)

            #down left
            for i in range(square+7, 64, 7):
                if i-7 in sq_bottom_edge or i-7 in sq_left_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece is not None and sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                if i in sq_left_edge or i in sq_bottom_edge:
                    valid.append(i)
                    break
                valid.append(i)

            #down right
            for i in range(square+9, 64, 9):
                if i-9 in sq_bottom_edge or i-9 in sq_right_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece is not None and sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                if i in sq_right_edge or i in sq_bottom_edge:
                    valid.append(i)
                    break
                valid.append(i)
            #endregion 
        if type == 'rook':
            # up
            for i in range(square-8, -1, -8):
                if i+8 in sq_top_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece is not None and sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                valid.append(i)
            # down
            for i in range(square+8, 64, 8):
                if i-8 in sq_bottom_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                valid.append(i)
            #right
            for i in range(square+1, 64, 1):
                if i-1 in sq_right_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                if i in sq_right_edge:
                    valid.append(i)
                    break
                valid.append(i)
                    
            #left
            for i in range(square-1, -1, -1):
                if i+1 in sq_left_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                if i in sq_left_edge:
                    valid.append(i)
                    break
                valid.append(i)
        if type == 'bishop':
            # up right
            for i in range(square-7, -1, -7):
                if i+7 in sq_top_edge or i+7 in sq_right_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece is not None and sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                if i in sq_right_edge or i in sq_top_edge:
                    valid.append(i)
                    break
                valid.append(i)

            # up left
            for i in range(square-9, -1, -9):
                if i+9 in sq_top_edge or i+9 in sq_left_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece is not None and sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                if i in sq_left_edge or i in sq_top_edge:
                    valid.append(i)
                    break
                valid.append(i)

            #down left
            for i in range(square+7, 64, 7):
                if i-7 in sq_bottom_edge or i-7 in sq_left_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece is not None and sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                if i in sq_left_edge or i in sq_bottom_edge:
                    valid.append(i)
                    break
                valid.append(i)

            #down right
            for i in range(square+9, 64, 9):
                if i-9 in sq_bottom_edge or i-9 in sq_right_edge:
                    break
                if sq[i].occupied_piece is not None:
                    if sq[i].occupied_piece is not None and sq[i].occupied_piece.color != color:
                        valid.append(i)
                    break
                if i in sq_right_edge or i in sq_bottom_edge:
                    valid.append(i)
                    break
                valid.append(i)
        if type == 'knight':
            potential_moves = [square-17, square-15, square-10, square-6, square+6, square+10, square+15, square+17]
            valid = [move for move in potential_moves if 0 <= move < 64 and (sq[move].occupied_piece is None or sq[move].occupied_piece.color != color)]
            sq_l = []
            sq_r = []
            sq_t = []
            sq_d = []
            for i in sq_left_edge:
                sq_l.append(i+1)
            for i in sq_right_edge:
                sq_r.append(i-1)
            for i in sq_top_edge:
                sq_t.append(i+8)
            for i in sq_bottom_edge:
                sq_d.append(i-8)

            if square in sq_left_edge:
                rm = [square-17, square+15, square-10, square+6]
                valid = [x for x in valid if x not in rm]
            if square in sq_l:
                rm = [square-10, square+6]
                valid = [x for x in valid if x not in rm]
            if square in sq_right_edge:
                rm = [square-15, square+17, square-6, square+10]
                valid = [x for x in valid if x not in rm]
            if square in sq_r:
                rm = [square+10, square-6]
                valid = [x for x in valid if x not in rm]
            if square in sq_top_edge:
                rm = [square-6, square-15, square-17, square-10]
                valid = [x for x in valid if x not in rm]
            if square in sq_t:
                rm = [square-6, square-10]
                valid = [x for x in valid if x not in rm]
            if square in sq_bottom_edge:
                rm = [square+15, square+17, square+6, square+10]
                valid = [x for x in valid if x not in rm]
            if square in sq_d:
                rm = [square+6, square+10]
                valid = [x for x in valid if x not in rm]
        if type =='pawn' and color == 'black':
            #move up one
            if sq[square+8].occupied_piece is None:
                valid.append(square+8)
            #move double
            if checking_piece.moved is False and sq[square+8].occupied_piece is None and sq[square+16].occupied_piece is None:
                valid.append(square+16)
            #capture right
            if sq[square+7].occupied_piece is not None and square not in sq_right_edge:
                if sq[square+7].occupied_piece.color == 'white':
                    valid.append(square+7)
            if sq[square+9].occupied_piece is not None and square not in sq_left_edge:
                if sq[square+9]. occupied_piece.color == 'white':
                    valid.append(square+9)
            if passant_l is True:
                valid.append(square+7)
            if passant_r is True:
                valid.append(square+9)
    if check is True:
        possible_moves = check_option(checking_piece, False, False, False, True)
        print("checkl")
        print(checking_piece.type)
        print(possible_moves)
        for move in possible_moves:
            print(move)
            if sq[move].occupied_piece in opponent_pieces:
                print("opponent piece")
                # Temporarily remove the captured piece to see if the king is still in check
                temp = sq[move].occupied_piece
                sq[move].occupied_piece = None

                # Simulate the move
                checking_piece.move(move, 0)
                sq[square].occupied_piece = None
                sq[move].occupied_piece = checking_piece
                if color == 'black':
                    white_pieces.remove(temp)
                else:
                    black_pieces.remove(temp)


                if check_check(state) is False:
                    print("valid")
                    valid.append(move)

                checking_piece.move(square, 0)
                sq[square].occupied_piece = checking_piece
                sq[move].occupied_piece = temp
                if color == 'black':
                    white_pieces.append(temp)
                if color == 'white':
                    black_pieces.append(temp)

            else:
                checking_piece.move(move, 0)
                sq[square].occupied_piece = None
                sq[move].occupied_piece = checking_piece
                check = check_check(state)
                if check_check(state) is False:
                    valid.append(move)
                checking_piece.move(square, 0)
                sq[square].occupied_piece = checking_piece
                sq[move].occupied_piece = None
            # Restoring the iteration state after each move
            restore_iteration_state()
        print(valid)

    # Restoring the board state after checking all possible moves
    restore_board_state()
    
    return valid

def draw_options(selected_piece, passant_l, passant_r, check):
    if selected_piece != None:
        options = check_option(selected_piece, passant_l, passant_r, check)
        options = check_check_check(options, selected_piece)                 
        for option in options:
            pygame.draw.circle(screen, 'gray', (sq[option].x_coord*90+45, sq[option].y_coord*90+45), 10)
                                

def check_check(game_state, depth=0):
    if game_state is 'white_selection':
        opponent_pieces = black_pieces
        color = 'white'
    else:
        opponent_pieces = white_pieces
        color = 'black'
        
    king_square = None
    for index, square in enumerate(sq):
        if square.occupied_piece is not None and square.occupied_piece.type == 'king' and square.occupied_piece.color == color:
            king_square = index
            break
    
    if king_square is not None:
        king_piece = sq[king_square].occupied_piece
        for piece in opponent_pieces:
            if piece.location != king_piece.location:
                options = check_option(piece, False, False, False, depth)
                if king_square in options:
                    return True
        
    return False


def check_mate(game_state, passant_l, passant_r):
    if game_state == 'black_selection':
        oponnent_pieces = white_pieces
        pieces = black_pieces
    else:
        oponnent_pieces = black_pieces
        pieces = white_pieces



    for piece in pieces:
        options = check_option(piece, passant_l, passant_r, False)
        if options != []:
            return False
    
    return True



def display_text(text, font_size, x, y, text_color=(0, 0, 0)):

    # Set up fonts
    font = pygame.font.SysFont(None, font_size)

    # Render the text on a surface
    text_surface = font.render(text, True, text_color)

    # Get the position to center the text
    text_x = x - text_surface.get_width() // 2
    text_y = y - text_surface.get_height() // 2

    # Blit the text surface onto the screen
    screen.blit(text_surface, (text_x, text_y))

    # Update the display
    pygame.display.update()

def display_result(result):
    pygame.init()
    screen = pygame.display.set_mode((1080, 720))
    pygame.display.set_caption("Chess Game Result")
    font = pygame.font.SysFont(None, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        if result == 'White wins!':
            screen.fill((255, 255, 255))
            text_surface = font.render(result, True, (0, 0, 0))
            text_x = (1080 - text_surface.get_width()) // 2
            text_y = (720 - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
        elif result == 'Black wins!':
            screen.fill((0, 0, 0))
            text_surface = font.render(result, True, (255, 255, 255))
            text_x = (1080 - text_surface.get_width()) // 2
            text_y = (720 - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
        else:
            screen.fill((128, 128, 128))
            text_surface = font.render(result, True, (255, 255, 255))
            text_x = (1080 - text_surface.get_width()) // 2
            text_y = (720 - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
        pygame.display.update()



def check_check_check(valid, checking_piece):
    initial_board_state = []
    for i in range(64):
        if sq[i].occupied_piece != None:
            if sq[i].occupied_piece.is_promo_piece == False:
                initial_board_state.append(sq[i].occupied_piece)
            else:
                initial_board_state.append(None)
        else:
            initial_board_state.append(sq[i].occupied_piece)
    def restore_board_state():
        for i in range(64):
            sq[i].occupied_piece = initial_board_state[i]
    if checking_piece is not None:
        color = checking_piece.color
        square = checking_piece.location
        if color == 'black':
            state = 'black_selection'
            opponent_pieces = white_pieces
        else:
            state = 'white_selection'
            opponent_pieces = black_pieces
        print(checking_piece.type)
        print(valid)
        temp = valid[:]
        for move in valid:
            temp_piece = None
            temp_piece = sq[move].occupied_piece
            checking_piece.move(move, 0)
            sq[square].occupied_piece = None
            sq[move].occupied_piece = checking_piece
            if temp_piece:
                if temp_piece.color == 'black':
                    try:
                        black_pieces.remove(temp_piece)
                    except:
                        pass
                else:
                    try:
                        white_pieces.remove(temp_piece)
                    except:
                        pass
            if check_check(state) is True:
                temp.remove(move)
            checking_piece.move(square, 0)
            sq[square].occupied_piece = checking_piece
            sq[move].occupied_piece = temp_piece
            if temp_piece:
                if temp_piece.color == 'black':
                    try:
                        black_pieces.append(temp_piece)
                    except:
                        pass
                else:
                    try:
                        white_pieces.append(temp_piece)
                    except:
                        pass
        restore_board_state()
        print(temp)
        return temp
    

def format_timer(remaining_time):
    minutes, seconds = divmod(remaining_time, 60)
    return f"{minutes:02d}:{seconds:02d}"

def draw_captured_pieces():
    for index, piece in enumerate(white_captured_pieces):
        if index < 8:
            screen.blit(piece.small, ((720+index*45), (630)))
        else:
            screen.blit(piece.small, ((720+(index-8)*45), (675)))
    for index, piece in enumerate(black_captured_pieces):
        if index < 8:
            screen.blit(piece.small, ((720+index*45), (45)))
        else:
            screen.blit(piece.small, ((720+(index-8)*45), (0)))

def update_timer():
    global player1_timer, player2_timer, timer_active

    if timer_active == 1:
        player1_timer -= clock.get_time()
        if player1_timer <= 0:
            print("Player 2 wins!")
            pygame.quit()
            sys.exit()

    elif timer_active == 2:
        player2_timer -= clock.get_time()
        if player2_timer <= 0:
            print("Player 1 wins!")
            pygame.quit()
            sys.exit()

def switch_timer():
    global timer_active
    if timer_active == 1:
        timer_active = 2
    elif timer_active == 2:
        timer_active = 1

def draw_timers():
    FONT_SIZE = 90
    font = pygame.font.Font(None, FONT_SIZE)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    player1_text_line1 = font.render("Player 1", True, BLACK)
    player1_text_line2 = font.render("{:.2f}".format(player1_timer / 1000), True, BLACK)
    player2_text_line1 = font.render("Player 2", True, WHITE)
    player2_text_line2 = font.render("{:.2f}".format(player2_timer / 1000), True, WHITE)

    player1_rect = pygame.Rect(720, 360, 360, 360)
    player2_rect = pygame.Rect(720, 0, 360, 360)
    pygame.draw.rect(screen, WHITE, player1_rect)
    pygame.draw.rect(screen, BLACK, player2_rect)



    #screen.blit(player1_text_line1, (810, 450))
    screen.blit(player1_text_line2, (810, 450))
    #screen.blit(player2_text_line1, (810, 270))
    screen.blit(player2_text_line2, (810, 180))

main()