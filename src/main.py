import dearpygui.dearpygui as dpg
from merger import merge_pdfs

class App:

    def __init__(self):
        self.file_list = []

    def add_pdf(self, file_path):
        self.file_list.append(file_path)
        with dpg.group(horizontal=True, parent="file_registry", tag=file_path):
            dpg.add_text(file_path)
            dpg.add_button(label="Remove", callback=lambda sender, app_data: self.remove_pdf(file_path))

    def remove_pdf(self, file_path):
        self.file_list.remove(file_path)
        dpg.delete_item(file_path)

    def init_windows(self):

        dpg.create_context()
        dpg.create_viewport(title='PDF merger', width=600, height=600)

        def callback(sender, app_data):
            for file_path in app_data['selections'].values():
                self.add_pdf(file_path)

        # function to show file picker dialog
        def show_file_picker(sender):
            dpg.show_item("file_dialog_id")

        # file picker dialog creation
        with dpg.file_dialog(directory_selector=False, show=False, callback=callback, tag="file_dialog_id", width=400, height=500):
            dpg.add_file_extension(".pdf", color=(0, 255, 0, 255), custom_text="[Pdf]")

        # drag-and-drop callback
        def drop_callback(sender, app_data, user_data):
            file_path = app_data
            self.add_pdf(file_path)

        with dpg.window(label="PDF Merge") as main_window:
            dpg.add_text("Files to merge:")
            with dpg.child_window(tag="file_registry", autosize_x=True, height=200):
                dpg.add_button(label="Add PDF", callback=show_file_picker)
            dpg.add_button(label="Merge PDFs")
            dpg.set_primary_window(main_window, True)


app = App()
app.init_windows()
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()