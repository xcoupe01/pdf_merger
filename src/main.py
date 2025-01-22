import dearpygui.dearpygui as dpg
import DearPyGui_DragAndDrop as dpg_dnd
import webbrowser
from merger import merge_pdfs
import json
import subprocess
import sys
import os
import tempfile
from tkinter.filedialog import askdirectory, askopenfilenames
import re

class App:

    def __init__(self):
        self.file_list = []
        self.pages_text = []
        self.output_folder = self.load_output_folder()

    def save_output_folder(self):
        data = {
            "output_folder": self.output_folder
        }
        with open("settings.json", "w") as f:
            json.dump(data, f)

    def load_output_folder(self):
        try:
            with open("settings.json", "r") as f:
                data = json.load(f)
                return data["output_folder"]
        except FileNotFoundError:
            return ""

    def add_pdf(self, file_path):
        self.file_list.append(file_path)
        self.pages_text.append("All")
        self.draw_file_registry()

    def write_pages(self):
        for i in range(len(self.pages_text)):
            self.pages_text[i] = dpg.get_value(f"pagesfi-{i}")

    def draw_file_registry(self):

        def drop_cb(sender, app_data, user_data):
            # sender is group, app_data is btn_drag
            self.write_pages()
            self.file_list[app_data], self.file_list[dpg.get_item_user_data(sender)] = self.file_list[dpg.get_item_user_data(sender)], self.file_list[app_data]
            self.pages_text[app_data], self.pages_text[dpg.get_item_user_data(sender)] = self.pages_text[dpg.get_item_user_data(sender)], self.pages_text[app_data]
            self.draw_file_registry()

        dpg.delete_item("file_registry", children_only=True)
        for i, file_path in enumerate(self.file_list):
            with dpg.group(horizontal=True, parent="file_registry", payload_type="file", drop_callback=drop_cb, user_data=i) as file_grp:
                dpg.add_image_button(texture_tag="arrow_up_icon", callback=self.move_pdf_up, user_data=i, height=13, width=13)
                dpg.add_text(file_path)
                dpg.add_text("pages: ")
                dpg.add_input_text(tag=f"pagesfi-{i}", default_value=self.pages_text[i], width=50)
                dpg.add_image_button(texture_tag="trashcan_icon", callback=self.remove_pdf, user_data=i, height=13, width=13)

                with dpg.drag_payload(parent=file_grp, drag_data=i, payload_type="file"):
                    dpg.add_text(f"dragging file {file_path}")
            
        # function to show file picker dialog
        def show_file_picker(sender):
            filetypes = (
                ('Pdf files', '*.pdf'),)
            
            filenames = askopenfilenames(
                title='Open a file',
                initialdir='/',
                filetypes=filetypes)

            for file in filenames:
                self.add_pdf(file)
            
        dpg.add_button(label="Add PDF", callback=show_file_picker, parent="file_registry")

    def move_pdf_up(self, sender, app_data, user_data):
        index = user_data
        if index > 0:
            self.write_pages()
            self.file_list[index], self.file_list[index - 1] = self.file_list[index - 1], self.file_list[index]
            self.pages_text[index], self.pages_text[index - 1] = self.pages_text[index - 1], self.pages_text[index]
            self.draw_file_registry()

    def remove_pdf(self, sender, app_data, user_data):
        self.write_pages()
        del self.file_list[user_data]
        del self.pages_text[user_data]
        self.draw_file_registry()

    def process_f_pages(self) -> list[list[int] | str]:
        f_pages = []
        for i in range(len(self.file_list)):
            pages = dpg.get_value(f"pagesfi-{i}")
            if pages == "All":
                f_pages.append("All")
                continue
            f_pages.append([])
            try:
                pages = pages.split(",")
                for page in pages:
                    if "-" in page:
                        page_range = page.split("-")
                        if len(page_range) != 2:
                            self.show_error("Invalid page numbers")
                            return []
                        start, end = int(page_range[0]), int(page_range[1])
                        if start > end:
                            self.show_error("Invalid page numbers")
                            return []
                        f_pages[-1] += list(range(start - 1, end))
                    else:
                        f_pages[-1].append(int(page) - 1)
            except ValueError:
                self.show_error("Invalid page numbers")
                return []
        return f_pages

    def merge_pdfs(self, sender, app_data):
        out_f = tempfile.gettempdir() if self.output_folder == "" else self.output_folder

        regex = re.compile(r'merged(\d*)\.pdf')
        matching_files = [f for f in os.listdir(out_f) if regex.match(f)]
        number = max([int(regex.match(f).group(1)) for f in matching_files if regex.match(f).group(1).isdigit()], default=0) + 1
        target_file = os.path.join(out_f, f"merged{number}.pdf")

        if len(self.file_list) < 2:
            self.show_error("Not enough files to merge")
            return
        for file in self.file_list:
            if not file.endswith(".pdf"):
                self.show_error("Only PDF files can be merged")
                return
        f_pages = self.process_f_pages()
        if f_pages == []:
            return
        merge_pdfs(self.file_list, target_file, f_pages)
        if self.output_folder == "":
            subprocess.Popen([target_file],shell=True)

    def show_error(self, message):
        dpg.set_value("error_text", message)
        dpg.configure_item("error_modal_id", show=True)

    def init_windows(self):

        def show_folder_picker(sender):
            self.output_folder = askdirectory(title='Select Folder')
            dpg.set_value("out_f_text", "Output folder: " + self.output_folder)
            self.save_output_folder()

        dpg.create_context()
        dpg_dnd.initialize()
        dpg.create_viewport(title='PDF merger', width=600, height=600)

        def file_pick_call(sender, app_data):
            for file_path in app_data['selections'].values():
                self.add_pdf(file_path)

        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        with dpg.texture_registry():
            width, height, channels, data = dpg.load_image(os.path.join(base_path, "img/trashcan.png"))
            dpg.add_static_texture(width, height, data, tag="trashcan_icon")
            width, height, channels, data = dpg.load_image(os.path.join(base_path, "img/uparrow.png"))
            dpg.add_static_texture(width, height, data, tag="arrow_up_icon")

        # file picker dialog creation
        with dpg.file_dialog(directory_selector=False, show=False, callback=file_pick_call, tag="file_dialog_id", width=400, height=500):
            dpg.add_file_extension(".pdf", color=(0, 255, 0, 255), custom_text="[Pdf]")

        with dpg.window(label="PDF Merge") as main_window:

            with dpg.menu_bar():
                with dpg.menu(label="Help"):
                    dpg.add_menu_item(label="How to use", callback=lambda: dpg.configure_item("howto_modal_id", show=True))
                    dpg.add_menu_item(label="About", callback=lambda: dpg.configure_item("about_modal_id", show=True))

            dpg.add_text("Files to merge:")
            with dpg.child_window(tag="file_registry", autosize_x=True, height=400):
                dpg_dnd.set_drop(self.drop)
            dpg.add_button(label="Merge PDFs", callback=self.merge_pdfs)
            # add button to show folder picker dialog
            dpg.add_button(label="Set output Folder", callback=show_folder_picker)
            dpg.add_text(f"Output folder: {self.output_folder if self.output_folder else 'Not picked!!'}", tag="out_f_text")
            
            with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left, modal=True, tag="howto_modal_id"):
                dpg.add_text("1. To merge PDFs, drag and drop the files in the window.\n\tYou can also use the 'Add PDF' button to select files.\n")
                dpg.add_text("2. To change the order of the files, use the 'Up' button\n\tto move the file upwards in the final document.\n\tThe file order represents the document order in the final document\n")
                dpg.add_text("3. To remove a file from the list, use the 'Remove' button.\n")
                dpg.add_text("4. To set the output folder, click the 'Set output Folder' button.\n\tNote that the will be shown right bellow this button.\n\tThe output file will be named 'merged.pdf'\n\tand will be placed in the chosed folder.\n\tThe folder must be selected before merging.\n")
                dpg.add_text("5. To merge the PDFs, click the 'Merge PDFs' button.\n")
                dpg.add_text("6. If you like the app, consider supporting the project\n\tby clicking the button below.\n")
                # vertical space
                dpg.add_text("")
                dpg.add_separator()
                dpg.add_text("")

                dpg.add_button(label="Support the project", callback=lambda: webbrowser.open("https://example.com"))
                dpg.configure_item("howto_modal_id", pos=(dpg.get_viewport_width() // 2 - 260, dpg.get_viewport_height() // 2 - 200))

            with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left, modal=True, tag="about_modal_id"):
                dpg.add_text("PDF Merger v1.0")
                dpg.add_text("Developed by: Vojtech Coupek")
                dpg.add_text("Used packages: PyPDF2, DearPyGui")
                dpg.configure_item("about_modal_id", pos=(dpg.get_viewport_width() // 2 - 200, dpg.get_viewport_height() // 2 - 100))

            with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left, modal=True, tag="error_modal_id"):
                dpg.add_text("Error occurred", tag="error_text")
                dpg.configure_item("error_modal_id", pos=(dpg.get_viewport_width() // 2 - 150, dpg.get_viewport_height() // 2 - 100))

            dpg.set_primary_window(main_window, True)
            self.draw_file_registry()


    def drop(self, data, keys):
        for file in data:
            self.add_pdf(file)

app = App()
app.init_windows()
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()