import dearpygui.dearpygui as dpg
import DearPyGui_DragAndDrop as dpg_dnd
import webbrowser
from merger import merge_pdfs

class App:

    def __init__(self):
        self.file_list = []
        self.output_folder = ""

    def add_pdf(self, file_path):
        self.file_list.append(file_path)
        self.draw_file_registry()

    def draw_file_registry(self):
        dpg.delete_item("file_registry", children_only=True)
        for file_path in self.file_list:
            with dpg.group(horizontal=True, parent="file_registry"):
                dpg.add_button(label="Up", callback=self.move_pdf_up, user_data=file_path)
                dpg.add_text(file_path)
                dpg.add_button(label="Remove", callback=self.remove_pdf, user_data=file_path)
            
        # function to show file picker dialog
        def show_file_picker(sender):
            dpg.show_item("file_dialog_id")
        dpg.add_button(label="Add PDF", callback=show_file_picker, parent="file_registry")

    def move_pdf_up(self, sender, app_data, user_data):
        file_path = user_data
        index = self.file_list.index(file_path)
        if index > 0:
            self.file_list[index], self.file_list[index - 1] = self.file_list[index - 1], self.file_list[index]
            self.draw_file_registry()

    def remove_pdf(self, sender, app_data, user_data):
        file_path = user_data
        self.file_list.remove(file_path)
        self.draw_file_registry()

    def merge_pdfs(self, sender, app_data):
        if self.output_folder == "":
            self.show_error("Output folder not set")
            return
        if len(self.file_list) < 2:
            self.show_error("Not enough files to merge")
            return
        for file in self.file_list:
            if not file.endswith(".pdf"):
                self.show_error("Only PDF files can be merged")
                return
        merge_pdfs(self.file_list, self.output_folder + "\\merged.pdf")

    def show_error(self, message):
        dpg.set_value("error_text", message)
        dpg.configure_item("error_modal_id", show=True)

    def init_windows(self):

        def show_folder_picker(sender):
            dpg.show_item("folder_dialog_id")

        dpg.create_context()
        dpg_dnd.initialize()
        dpg.create_viewport(title='PDF merger', width=600, height=600)

        def file_pick_call(sender, app_data):
            for file_path in app_data['selections'].values():
                self.add_pdf(file_path)
        
        def folder_pick_call(sender, app_data):
            if app_data['selections'].values() == []:
                return
            self.output_folder = app_data['file_path_name']
            print(app_data)
            dpg.set_value("out_f_text", "Output folder: " + self.output_folder)

        # file picker dialog creation
        with dpg.file_dialog(directory_selector=False, show=False, callback=file_pick_call, tag="file_dialog_id", width=400, height=500):
            dpg.add_file_extension(".pdf", color=(0, 255, 0, 255), custom_text="[Pdf]")

        dpg.add_file_dialog(directory_selector=True, show=False, callback=folder_pick_call, tag="folder_dialog_id", width=400, height=500)

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
            dpg.add_text("Output folder: Not picked!!", tag="out_f_text")
            
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