import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QTabWidget, QVBoxLayout, QLabel,
    QListWidget, QTreeWidget, QTreeWidgetItem,
    QPushButton, QHBoxLayout, QInputDialog,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtGui import QIcon
from database import initialize_database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.setWindowTitle("Qurupeco")
        self.resize(900, 600)

        # Initialize DB when app opens
        initialize_database()

        # Main tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # -----------------------------------------------------------
        # WATCH TAB
        # -----------------------------------------------------------
        self.watch_tab = QWidget()
        self.watch_layout = QVBoxLayout(self.watch_tab)
        
        self.load_button = QPushButton("Load")
        self.watch_layout.addWidget(self.load_button)
        self.load_button.clicked.connect(self.load_files)

        # Movies section
        self.movies_label = QLabel("Movies")
        self.movies_list = QListWidget()
        self.movies_list.itemClicked.connect(self.on_movie_clicked)

        # Series section
        self.series_label = QLabel("Series")
        self.series_tree = QTreeWidget()
        self.series_tree.setHeaderLabels(["Series / Episodes"])
        self.series_tree.itemClicked.connect(self.on_tv_clicked)


        # Add to Watch layout
        self.watch_layout.addWidget(self.movies_label)
        self.watch_layout.addWidget(self.movies_list)
        self.watch_layout.addWidget(self.series_label)
        self.watch_layout.addWidget(self.series_tree)

        # -----------------------------------------------------------
        # DATA TAB (blank for now)
        # -----------------------------------------------------------
        # -----------------------------------------------------------
        # DATA TAB (Movies + TV)
        # -----------------------------------------------------------
        self.data_tab = QWidget()
        self.data_layout = QVBoxLayout(self.data_tab)

        self.data_tabs = QTabWidget()  # inner tab widget

        # Movies table
        self.movies_table = QTableWidget()
        self.movies_table.setColumnCount(2)
        self.movies_table.setHorizontalHeaderLabels(["Filename", "Movie Name"])

        # TV table
        self.tv_table = QTableWidget()
        self.tv_table.setColumnCount(4)
        self.tv_table.setHorizontalHeaderLabels(["Filename", "Series Name", "Season", "Episode"])

        self.data_tabs.addTab(self.movies_table, "Movies")
        self.data_tabs.addTab(self.tv_table, "TV Shows")

        self.data_layout.addWidget(self.data_tabs)

        self.delete_movie_btn = QPushButton("Delete Selected Movie")
        self.delete_tv_btn = QPushButton("Delete Selected TV Entry")

        btn_data_layout = QHBoxLayout()
        btn_data_layout.addWidget(self.delete_movie_btn)
        btn_data_layout.addWidget(self.delete_tv_btn)

        self.data_layout.addLayout(btn_data_layout)

        self.delete_movie_btn.clicked.connect(self.delete_selected_movie)
        self.delete_tv_btn.clicked.connect(self.delete_selected_tv)



        # -----------------------------------------------------------
        # PATHS TAB
        # -----------------------------------------------------------
        self.paths_tab = QWidget()
        self.paths_layout = QVBoxLayout(self.paths_tab)

        self.paths_list = QListWidget()

        # Buttons
        self.add_path_btn = QPushButton("Add Path")
        self.edit_path_btn = QPushButton("Edit Selected Path")
        self.remove_path_btn = QPushButton("Remove Selected Path")
        self.scan_btn = QPushButton("Scan")

        # Layout for buttons
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_path_btn)
        btn_layout.addWidget(self.edit_path_btn)
        btn_layout.addWidget(self.remove_path_btn)
        btn_layout.addWidget(self.scan_btn)

        self.paths_layout.addWidget(self.paths_list)
        self.paths_layout.addLayout(btn_layout)

        # Found files label + list
        self.found_label = QLabel("Found Files:")
        self.found_files_list = QListWidget()
        self.found_files_list.setSpacing(4)

        self.paths_layout.addWidget(self.found_label)
        self.paths_layout.addWidget(self.found_files_list)

        # Add tabs
        self.tabs.addTab(self.watch_tab, "Watch")
        self.tabs.addTab(self.data_tab, "Data")
        self.tabs.addTab(self.paths_tab, "Paths")

        self.filemap = {}  # filename → full path
        # Load Watch tab immediately
        self.load_watch_tab()

        # Connect tab change
        self.tabs.currentChanged.connect(self.on_tab_change)

        # Connect buttons
        self.add_path_btn.clicked.connect(self.add_path_clicked)
        self.edit_path_btn.clicked.connect(self.edit_path_clicked)
        self.remove_path_btn.clicked.connect(self.remove_path_clicked)
        self.scan_btn.clicked.connect(self.scan_paths)
        self.movies_table.cellChanged.connect(self.movie_cell_changed)
        self.tv_table.cellChanged.connect(self.tv_cell_changed)

        


        # Styles
        self.setStyleSheet("""
            QTabBar::tab {
                background: #444;
                color: white;
                padding: 8px 12px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: #d35400;
                color: white;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #ddd;
            }
        """)

    # -----------------------------------------------------------
    # WATCH TAB DATA LOADING
    # -----------------------------------------------------------
    def load_watch_tab(self):
        """Load movies and series from database into the Watch tab."""
        from database import get_all_movies, get_all_tv_entries

        # Clear current lists
        self.movies_list.clear()
        self.series_tree.clear()

        # ----- Load Movies -----
        movies = get_all_movies()
        for filename, movieName in movies:
            label = movieName
            if filename not in self.filemap:
                label += "   (MISSING)"
            self.movies_list.addItem(label)


        # ----- Load TV entries -----
        tv_entries = get_all_tv_entries()

        # Build a dict: seriesName → list of (season, episode, filename)
        series_dict = {}
        for filename, seriesName, season, episode in tv_entries:
            if seriesName not in series_dict:
                series_dict[seriesName] = []
            series_dict[seriesName].append((season, episode, filename))

        # Create series/episode tree
        for seriesName, episodes in series_dict.items():
            series_item = QTreeWidgetItem([seriesName])
            self.series_tree.addTopLevelItem(series_item)

            for season, episode, filename in episodes:
                episode_text = f"S{season:02d}E{episode:02d}"
                if filename not in self.filemap:
                    episode_text += "   (MISSING)"
                QTreeWidgetItem(series_item, [episode_text])


    # -----------------------------------------------------------
    # PATHS TAB LOGIC
    # -----------------------------------------------------------
    def load_paths(self):
        from database import get_paths
        self.paths_list.clear()
        for p in get_paths():
            self.paths_list.addItem(p)

    def add_path_clicked(self):
        from database import add_path
        path, ok = QInputDialog.getText(self, "Add Path", "Enter directory path:")
        if ok and path.strip():
            add_path(path.strip())
            self.load_paths()

    def edit_path_clicked(self):
        from database import update_path
        item = self.paths_list.currentItem()
        if not item:
            return

        old_path = item.text()
        new_path, ok = QInputDialog.getText(self, "Edit Path", "Edit path:", text=old_path)
        if ok and new_path.strip():
            update_path(old_path, new_path.strip())
            self.load_paths()

    def remove_path_clicked(self):
        from database import remove_path
        item = self.paths_list.currentItem()
        if not item:
            return

        remove_path(item.text())
        self.load_paths()

    # -----------------------------------------------------------
    # TAB SWITCH EVENT
    # -----------------------------------------------------------
    def on_tab_change(self, index):
        # Watch tab = 0
        if index == 0:
            self.load_watch_tab()

        # Data tab = 1 (unused for now)
        if index == 1:  # Data tab
            self.load_movies_table()
            self.load_tv_table()


        # Paths tab = 2
        if index == 2:
            self.load_paths()

    def scan_paths(self):
        """Scan all paths in the database for .mp4 and .mkv files."""
        import os
        from database import get_paths

        self.found_files_list.clear()

        paths = get_paths()
        video_extensions = (".mp4", ".mkv")

        found = []

        for path in paths:
            if not os.path.isdir(path):
                continue

            # Walk the directory
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith(video_extensions):
                        from database import filename_exists

                        full_path = os.path.join(root, file)

                        # don’t include files already in DB
                        if not filename_exists(file):
                            found.append(full_path)

        # Display results
        for f in found:
            self.add_found_file_item(f)

    def add_found_file_item(self, filepath):
        """Add a found file with a 'Create Entry' button."""
        from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QListWidgetItem

        # Container widget for the row
        row_widget = QWidget()
        layout = QHBoxLayout(row_widget)
        layout.setContentsMargins(4, 2, 4, 2)

        label = QLabel(filepath)
        button = QPushButton("Create Entry")

        layout.addWidget(label)
        layout.addWidget(button)

        # Add to the list widget
        item = QListWidgetItem()
        item.setSizeHint(row_widget.sizeHint())

        self.found_files_list.addItem(item)
        self.found_files_list.setItemWidget(item, row_widget)

        # Connect button
        button.clicked.connect(lambda: self.create_entry_dialog(filepath))

    def create_entry_dialog(self, filepath):
        """Dialog to create a Movie or TV entry from a file."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
        import os

        dialog = QDialog(self)
        dialog.setWindowTitle("Create Entry")
        layout = QVBoxLayout(dialog)

        # Movie or TV selection
        type_label = QLabel("Type:")
        type_select = QComboBox()
        type_select.addItems(["Movie", "TV Episode"])

        layout.addWidget(type_label)
        layout.addWidget(type_select)

        # Fields for movie
        movie_name_label = QLabel("Movie Name:")
        movie_name_input = QLineEdit()

        # Fields for TV
        series_name_label = QLabel("Series Name:")
        series_name_input = QLineEdit()

        season_label = QLabel("Season:")
        season_input = QLineEdit()

        episode_label = QLabel("Episode:")
        episode_input = QLineEdit()

        # Add all but hide TV fields initially
        layout.addWidget(movie_name_label)
        layout.addWidget(movie_name_input)

        layout.addWidget(series_name_label)
        layout.addWidget(series_name_input)
        layout.addWidget(season_label)
        layout.addWidget(season_input)
        layout.addWidget(episode_label)
        layout.addWidget(episode_input)

        # Hide TV fields at first
        series_name_label.hide()
        series_name_input.hide()
        season_label.hide()
        season_input.hide()
        episode_label.hide()
        episode_input.hide()

        # Switch UI depending on Movie / TV selection
        def on_type_change(index):
            if index == 0:  # Movie
                movie_name_label.show()
                movie_name_input.show()

                series_name_label.hide()
                series_name_input.hide()
                season_label.hide()
                season_input.hide()
                episode_label.hide()
                episode_input.hide()

            else:  # TV Episode
                movie_name_label.hide()
                movie_name_input.hide()

                series_name_label.show()
                series_name_input.show()
                season_label.show()
                season_input.show()
                episode_label.show()
                episode_input.show()

        type_select.currentIndexChanged.connect(on_type_change)

        # Save button
        save_button = QPushButton("Save Entry")
        layout.addWidget(save_button)

        # Handle save click
        def save():
            filename = os.path.basename(filepath)

            if type_select.currentIndex() == 0:  # Movie
                from database import add_movie_entry
                add_movie_entry(filename, movie_name_input.text().strip())
            else:  # TV
                from database import add_tv_entry
                add_tv_entry(
                    filename,
                    series_name_input.text().strip(),
                    int(season_input.text()),
                    int(episode_input.text())
                )

            dialog.accept()
            self.load_watch_tab()  # Refresh the Watch tab

        save_button.clicked.connect(save)

        dialog.exec()

    def load_movies_table(self):
        from database import get_all_movies
        movies = get_all_movies()

        self.movies_table.setRowCount(len(movies))
        for row, (filename, movieName) in enumerate(movies):
            self.movies_table.setItem(row, 0, QTableWidgetItem(filename))
            self.movies_table.setItem(row, 1, QTableWidgetItem(movieName))

    def load_tv_table(self):
        from database import get_all_tv_entries
        tv_entries = get_all_tv_entries()

        self.tv_table.setRowCount(len(tv_entries))
        for row, (filename, seriesName, season, episode) in enumerate(tv_entries):
            self.tv_table.setItem(row, 0, QTableWidgetItem(filename))
            self.tv_table.setItem(row, 1, QTableWidgetItem(seriesName))
            self.tv_table.setItem(row, 2, QTableWidgetItem(str(season)))
            self.tv_table.setItem(row, 3, QTableWidgetItem(str(episode)))

    def movie_cell_changed(self, row, column):
        from database import update_movie_entry

        filename_item = self.movies_table.item(row, 0)
        movie_item = self.movies_table.item(row, 1)

        if not filename_item or not movie_item:
            return

        filename = filename_item.text()
        movieName = movie_item.text()

        update_movie_entry(filename, movieName)
        self.load_watch_tab()

    def tv_cell_changed(self, row, column):
        from database import update_tv_entry

        f = self.tv_table.item(row, 0)
        sname = self.tv_table.item(row, 1)
        season = self.tv_table.item(row, 2)
        episode = self.tv_table.item(row, 3)

        if not f or not sname or not season or not episode:
            return

        update_tv_entry(
            f.text(),
            sname.text(),
            int(season.text()),
            int(episode.text())
        )
        self.load_watch_tab()

    def delete_selected_movie(self):
        from database import delete_movie_entry

        row = self.movies_table.currentRow()
        if row < 0:
            return

        filename = self.movies_table.item(row, 0).text()
        delete_movie_entry(filename)
        self.load_movies_table()
        self.load_watch_tab()

    def delete_selected_tv(self):
        from database import delete_tv_entry

        row = self.tv_table.currentRow()
        if row < 0:
            return

        filename = self.tv_table.item(row, 0).text()
        delete_tv_entry(filename)
        self.load_tv_table()
        self.load_watch_tab()

    def load_files(self):
        """Match database filenames to real file paths in Pathlist."""
        import os
        from database import get_paths, get_all_movies, get_all_tv_entries

        self.filemap = {}  # reset

        paths = get_paths()
        all_entries = []

        # Get all filenames from movies
        for filename, movieName in get_all_movies():
            all_entries.append(filename)

        # Get all filenames from TV
        for filename, seriesName, season, episode in get_all_tv_entries():
            all_entries.append(filename)

        # Build a fast lookup table: filename → full path
        found_map = {}

        # Scan all paths
        for base in paths:
            if not os.path.isdir(base):
                continue

            for root, dirs, files in os.walk(base):
                for f in files:
                    if f in all_entries:
                        full_path = os.path.join(root, f)
                        found_map[f] = full_path

        # Store results
        self.filemap = found_map

        # Refresh Watch tab to apply missing markers
        self.load_watch_tab()

    def open_video(self, filename):
        """Open the video file using the system's default media player."""
        import os
        import subprocess
        import sys

        if filename not in self.filemap:
            return  # no path loaded

        path = self.filemap[filename]

        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):  # macOS
            subprocess.call(["open", path])
        else:  # Linux
            subprocess.call(["xdg-open", path])


    def on_movie_clicked(self, item):
        name = item.text().replace("   (MISSING)", "")
        
        # Find the filename for this movie
        from database import get_all_movies
        for filename, movieName in get_all_movies():
            if movieName == name:
                self.open_video(filename)
                break
    def on_tv_clicked(self, item, column):
        text = item.text(0).replace("   (MISSING)", "")

        # Skip top-level series names
        parent = item.parent()
        if parent is None:
            return

        seriesName = parent.text(0)

        # Parse "S01E02"
        season = int(text[1:3])
        episode = int(text[4:6])

        from database import get_all_tv_entries
        for filename, sname, s, e in get_all_tv_entries():
            if sname == seriesName and s == season and e == episode:
                self.open_video(filename)
                break








# -----------------------------------------------------------
# MAIN EXECUTION
# -----------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
