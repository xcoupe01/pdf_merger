import dearpygui.dearpygui as dpg
import DearPyGui_DragAndDrop as dpg_dnd
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
            print("Output folder not set")
            return
        if len(self.file_list) < 2:
            print("Not enough files to merge")
            return
        merge_pdfs(self.file_list, self.output_folder + "\\merged.pdf")

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
            dpg.add_text("Files to merge:")
            with dpg.child_window(tag="file_registry", autosize_x=True, height=200):
                dpg_dnd.set_drop(self.drop)
            dpg.add_button(label="Merge PDFs", callback=self.merge_pdfs)
            # add button to show folder picker dialog
            dpg.add_button(label="Set output Folder", callback=show_folder_picker)
            dpg.add_text("Output folder: Not picked!!", tag="out_f_text")
            
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