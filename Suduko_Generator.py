import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk 
import os

class SudokuGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Sudoku Generator")
        try:
            self.background_image = Image.open("suduko.png")
            self.background_photo = ImageTk.PhotoImage(self.background_image)

            self.background_label = tk.Label(master, image=self.background_photo)
            self.background_label.image = self.background_photo  # Keep a reference to avoid garbage collection
            self.background_label.place(relwidth=1, relheight=1)
        except FileNotFoundError:
            messagebox.showerror("Error", "Image file not found. Please provide a valid image file path.")
        input_frame = tk.Frame(master)
        input_frame.pack(side="top",pady=0)

        self.label = tk.Label(input_frame, text="Pick the Grid Size")
        self.label.pack(side="left")

        self.entry = tk.Entry(input_frame)
        self.entry.pack(side="left")

        self.generate_button = tk.Button(input_frame, text="Start Game", command=self.generate_sudoku, font=("Helvetica", 12, "bold"))
        self.generate_button.pack(side="left")
        
        difficulty_frame = tk.Frame(master)
        difficulty_frame.pack(side="top", pady=30)
        self.difficulty_label = tk.Label(difficulty_frame, text="Select Difficulty:")
        self.difficulty_label.pack(side="left")
        
        self.easy_button = tk.Button(difficulty_frame, text="Easy", command=lambda: self.set_and_generate_difficulty("easy"))
        self.easy_button.pack(side="left", padx=5)
        
        self.medium_button = tk.Button(difficulty_frame, text="Medium", command=lambda: self.set_and_generate_difficulty("medium"))
        self.medium_button.pack(side="left", padx=5)
       
        self.hard_button = tk.Button(difficulty_frame, text="Hard", command=lambda: self.set_and_generate_difficulty("hard"))
        self.hard_button.pack(side="left", padx=5)
        button_frame = tk.Frame(master)
        button_frame.place(relx=0.5, rely=0.95, anchor="center")
        self.solutions_button = tk.Button(button_frame, text="Solution Count", command=self.display_solution_count,font=("Helvetica", 12, "bold"))
        self.solutions_button.pack(side="left", padx=10)

        self.display_solution_button = tk.Button(button_frame, text="Show Solutions", command=self.display_solutions,font=("Helvetica", 12, "bold"))
        self.display_solution_button.pack(side="left", padx=10)
        self.quit_button = tk.Button(button_frame, text="Exit Game", command=self.quit_program,font=("Helvetica", 12, "bold"))
        self.quit_button.pack(side="left", padx=10)
        self.submit_button = None  # Initialize submit_button variable
        self.difficulty = None

        self.generated_sudoku = None
        self.sudoku_solutions = []
        self.solution_index = 0
        self.playing_sudoku = None
        self.current_cell = None
        self.playing_window = None
        
    def quit_program(self):
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to quit?")
        if confirmation:
            try:
                self.master.destroy()
            except Exception as e:
                print(f"Error while quitting: {e}")
            finally:
                os._exit(0)
    def set_and_generate_difficulty(self, difficulty):
        self.set_difficulty(difficulty)
        self.generate_sudoku()

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
    def generate_sudoku(self):
     try:
        size = int(self.entry.get())
        if size < 1:
            raise ValueError("Invalid input. Please enter a positive integer.")

        if self.difficulty is None:
            messagebox.showinfo("Error", "Please select a difficulty level first.")
            return

        # Show the difficulty level chosen
        messagebox.showinfo("Difficulty Selected", f"Difficulty set to {self.difficulty.capitalize()}")

        if self.difficulty == "easy":
            empty_cells = int(size * size * 0.35)
        elif self.difficulty == "medium":
            empty_cells = int(size * size * 0.5)
        elif self.difficulty == "hard":
            empty_cells = int(size * size * 0.65)
        else:
            raise ValueError("Invalid difficulty level")

        self.generated_sudoku = self.generate_sudoku_grid(size, empty_cells)
        self.sudoku_solutions = self.get_all_sudoku_solutions(self.generated_sudoku)
        self.solution_index = 0

        # Start the game immediately after generating Sudoku
        self.play_sudoku()

        # Clear the entry widget after generating Sudoku
        self.entry.delete(0, tk.END)

        # Clear the difficulty level after generating Sudoku
        self.difficulty = None

     except ValueError as e:
        messagebox.showerror("Error", str(e))
    def generate_sudoku_grid(self, n, empty_cells):
        grid = [[0] * n for _ in range(n)]
        self.solve_sudoku(grid)
        original_grid = [row[:] for row in grid]

        for _ in range(empty_cells):
            row, col = random.randint(0, n - 1), random.randint(0, n - 1)
            while grid[row][col] == 0:
                row, col = random.randint(0, n - 1), random.randint(0, n - 1)
            grid[row][col] = 0

        if self.get_sudoku_solution_count(original_grid) != 1:
            return self.generate_sudoku_grid(n, empty_cells)

        return grid


    def solve_sudoku(self, grid):
        empty = self.find_empty_location(grid)
        if not empty:
            return True
        row, col = empty

        for num in range(1, len(grid) + 1):
            if self.is_valid_move(grid, row, col, num):
                grid[row][col] = num

                if self.solve_sudoku(grid):
                    return True

                grid[row][col] = 0

        return False

    def find_empty_location(self, grid):
        for i in range(len(grid)):
            for j in range(len(grid)):
                if grid[i][j] == 0:
                    return i, j
        return None

    def is_valid_move(self, grid, row, col, num):
        if num in grid[row] or num in [grid[i][col] for i in range(len(grid))]:
            return False

        subgrid_size = int(len(grid) ** 0.5)
        start_row, start_col = subgrid_size * (row // subgrid_size), subgrid_size * (col // subgrid_size)

        for i in range(subgrid_size):
            for j in range(subgrid_size):
                if (
                    start_row + i < len(grid) and
                    start_col + j < len(grid[0]) and
                    grid[start_row + i][start_col + j] == num
                ):
                    return False

        return True


    def get_sudoku_solution_count(self, grid):
        solution_grid = [row[:] for row in grid]
        count = 0

        def count_solutions(grid):
            nonlocal count
            empty = self.find_empty_location(grid)
            if not empty:
                count += 1
                return
            row, col = empty

            for num in range(1, len(grid) + 1):
                if self.is_valid_move(grid, row, col, num):
                    grid[row][col] = num
                    count_solutions(grid)
                    grid[row][col] = 0

        count_solutions(solution_grid)
        return count

    def get_all_sudoku_solutions(self, grid):
        solutions = []
        def find_all_solutions(grid):
            empty = self.find_empty_location(grid)
            if not empty:
                solutions.append([row[:] for row in grid])
                return
            row, col = empty

            for num in range(1, len(grid) + 1):
                if self.is_valid_move(grid, row, col, num):
                    grid[row][col] = num
                    find_all_solutions(grid)
                    grid[row][col] = 0

        find_all_solutions(grid)
        return solutions
    def display_solution_count(self):
        if not self.generated_sudoku:
            messagebox.showinfo("Error", "Please generate a Sudoku first.")
            return
    
        solution_count = self.get_sudoku_solution_count(self.generated_sudoku)
    
        if solution_count == 0:
            messagebox.showinfo("Number of Solutions", "No solution found for the generated Sudoku.")
        elif solution_count == 1:
            messagebox.showinfo("Number of Solutions", "The Sudoku has a unique solution.")
        else:
            messagebox.showinfo("Number of Solutions", "The Sudoku has multiple solutions.")





    def display_solutions(self):
        if not self.generated_sudoku:
            messagebox.showinfo("Error", "Please generate a Sudoku first.")
            return

        if not self.sudoku_solutions:
            messagebox.showinfo("Error", "No solutions found for the generated Sudoku.")
            return

        if self.solution_index >= len(self.sudoku_solutions):
            messagebox.showinfo("All Solutions Displayed", "No more solutions to display.")
            return

        solution_grid = [row[:] for row in self.sudoku_solutions[self.solution_index]]
        self.display_sudoku_in_new_window(solution_grid, title=f"Solution {self.solution_index + 1}")
        self.solution_index += 1

    def play_sudoku(self):
        if not self.generated_sudoku:
            messagebox.showinfo("Error", "Please generate a Sudoku first.")
            return

        self.playing_sudoku = [row[:] for row in self.generated_sudoku]
        self.current_cell = [0, 0]

        if self.playing_window:
            self.playing_window.destroy()

        self.playing_window = tk.Toplevel(self.master)
        self.playing_window.title("Play Sudoku")

        # Display Sudoku in window
        self.display_sudoku_in_window(self.playing_window, self.playing_sudoku, play_mode=True)

        # Add a Submit button
        self.submit_button = tk.Button(self.playing_window, text="Submit", command=self.check_solution)
        self.submit_button.grid(row=len(self.playing_sudoku), column=0, columnspan=len(self.playing_sudoku[0]))


    def on_key_press(self, event):
        if not self.playing_sudoku:
            return

        if event.char.isdigit() and 1 <= int(event.char) <= len(self.playing_sudoku):
            self.playing_sudoku[self.current_cell[0]][self.current_cell[1]] = int(event.char)
            self.display_sudoku_in_window(self.playing_window, self.playing_sudoku, play_mode=True)

    def on_arrow_key_press(self, event):
        if not self.playing_sudoku:
            return

        if event.keysym in {"Up", "Down", "Left", "Right"}:
            row, col = self.current_cell
            if event.keysym == "Up" and row > 0:
                row -= 1
            elif event.keysym == "Down" and row < len(self.playing_sudoku) - 1:
                row += 1
            elif event.keysym == "Left" and col > 0:
                col -= 1
            elif event.keysym == "Right" and col < len(self.playing_sudoku[0]) - 1:
                col += 1

            self.current_cell = [row, col]
            self.display_sudoku_in_window(self.playing_window, self.playing_sudoku, play_mode=True)

    def on_cell_click(self, event, row, col, window, play_mode):
        if not play_mode:
            return

        self.current_cell = [row, col]
        self.display_sudoku_in_window(window, self.playing_sudoku, play_mode=True)

    def display_sudoku_in_window(self, window, grid, play_mode=False):
        # Check if the submit_button exists
        submit_button_exists = False
        for widget in window.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "Submit":
                submit_button_exists = True
                break

        # Clear the window
        for widget in window.winfo_children():
            widget.destroy()

        # Add the submit_button if it existed before clearing the window
        if submit_button_exists:
            self.submit_button = tk.Button(window, text="Submit", command=self.check_solution)
            self.submit_button.grid(row=len(grid), column=0, columnspan=len(grid[0]))

        # Rest of the method remains unchanged
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                cell_value = grid[i][j]
                background_color = "lightblue" if (i // 3 + j // 3) % 2 == 0 else "lightgreen"

                if play_mode and self.current_cell == [i, j]:
                    cell_label = tk.Label(window, text=str(cell_value) if cell_value != 0 else "",
                                           width=4, height=2, relief="solid", borderwidth=2,
                                           bg="yellow", fg="black")
                else:
                    cell_label = tk.Label(window, text=str(cell_value) if cell_value != 0 else "",
                                           width=4, height=2, relief="solid", borderwidth=1,
                                           bg=background_color, fg="black")

                cell_label.bind("<Button-1>", lambda event, i=i, j=j: self.on_cell_click(event, i, j, window, play_mode))
                cell_label.grid(row=i, column=j)

        if play_mode:
            window.bind("<Key>", self.on_key_press)
            window.bind("<Up>", self.on_arrow_key_press)
            window.bind("<Down>", self.on_arrow_key_press)
            window.bind("<Left>", self.on_arrow_key_press)
            window.bind("<Right>", self.on_arrow_key_press)

    def display_sudoku_in_new_window(self, grid, title="Generated Sudoku Puzzle", play_mode=False):
        new_window = tk.Toplevel(self.master)
        new_window.title(title)
       


        for i in range(len(grid)):
            for j in range(len(grid[0])):
                cell_value = grid[i][j]
                background_color = "lightblue" if (i // 3 + j // 3) % 2 == 0 else "lightgreen"

                if play_mode and self.current_cell == [i, j]:
                    cell_label = tk.Label(new_window, text=str(cell_value) if cell_value != 0 else "",
                                           width=4, height=2, relief="solid", borderwidth=2,
                                           bg="yellow", fg="black")
                else:
                    cell_label = tk.Label(new_window, text=str(cell_value) if cell_value != 0 else "",
                                           width=4, height=2, relief="solid", borderwidth=1,
                                           bg=background_color, fg="black")

                cell_label.bind("<Button-1>", lambda event, i=i, j=j: self.on_cell_click(event, i, j, new_window, play_mode))
                cell_label.grid(row=i, column=j)

        if play_mode:
            new_window.bind("<Key>", self.on_key_press)
            new_window.bind("<Up>", self.on_arrow_key_press)
            new_window.bind("<Down>", self.on_arrow_key_press)
            new_window.bind("<Left>", self.on_arrow_key_press)
            new_window.bind("<Right>", self.on_arrow_key_press)

    def check_solution(self):
        if not self.generated_sudoku:
            messagebox.showinfo("Error", "Please generate a Sudoku first.")
            return
        
        if not self.playing_sudoku:
            messagebox.showinfo("Error", "Please start playing the Sudoku.")
            return
        
        user_solution = [row[:] for row in self.playing_sudoku]
    
        # Check if the user solution matches any of the valid solutions
        if any(user_solution == solution for solution in self.sudoku_solutions):
            messagebox.showinfo("Result", "Valid Solution!")
        else:
            messagebox.showinfo("Result", "Invalid Solution. Try again.")
def main():
   root = tk.Tk()
   app = SudokuGeneratorApp(root)
   root.geometry("520x520") 
   root.resizable(False, False)
   root.mainloop()
if __name__ == "__main__":
    main()



