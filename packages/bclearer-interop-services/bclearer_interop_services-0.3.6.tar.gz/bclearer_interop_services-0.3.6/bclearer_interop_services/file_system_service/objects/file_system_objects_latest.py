import shutil
from pathlib import Path

from bclearer_core.configurations.datastructure.logging_inspection_level_b_enums import (
    LoggingInspectionLevelBEnums,
)
from bclearer_interop_services.file_system_service.objects.path_properties import (
    PathProperties,
)
from bclearer_interop_services.file_system_service.objects.wrappers.absolute_path_wrappers import (
    AbsolutePathWrappers,
)
from bclearer_orchestration_services.identification_services.uuid_service.uuid_helpers.uuid_factory import (
    create_new_uuid,
)


class FileSystemObjects:
    def __init__(
        self,
        absolute_path: Path = None,
        # TODO: absolute_path_string parameter to be deprecated in time.
        absolute_path_string: str = None,
        parent_folder: object = None,
    ):
        from bclearer_interop_services.file_system_service.objects.folders_latest import (
            Folders,
        )

        if (
            parent_folder
            and not isinstance(
                parent_folder, Folders
            )
        ):
            raise TypeError

        # TODO: Needs to be replaced by a creation of a bie id??
        self.uuid = create_new_uuid()

        if absolute_path:
            self.__path = (
                AbsolutePathWrappers(
                    absolute_path
                )
            )

        else:  # NOTE: If the path string is empty, it deals with it inside the PathWrappers class
            self.__path = (
                AbsolutePathWrappers(
                    absolute_path_string
                )
            )

        # self.parent_folder = \
        #     parent_folder

        # TODO: is it all this what should be moved out to the snapshot?
        #  Maybe the IndividualFileSystemSnapshotObjects?
        if self.__path.exists():
            self.file_system_object_properties = PathProperties(
                input_file_system_object_path=self.__path.absolute_path_string
            )

    @property
    def parent_folder(self):
        from bclearer_interop_services.file_system_service.objects.folders import (
            Folders,
        )

        return Folders(
            absolute_path_string=self.__path.parent
        )

    @property
    def base_name(self) -> str:
        return self.__path.base_name

    @property
    def file_stem_name(self) -> str:
        return (
            self.__path.file_stem_name
        )

    @property
    def absolute_path_string(
        self,
    ) -> str:
        return (
            self.__path.absolute_path_string
        )

    @property
    def absolute_path(self) -> Path:
        path = self.__path.path

        return path

    @property
    def absolute_level(self) -> int:
        return (
            self.__path.absolute_level
        )

    @property
    def parent_absolute_path_string(
        self,
    ) -> str:
        return str(self.__path.parent)

    # TODO: should we move this method only to Folders? As Files shouldn't be able to do this
    # TODO: Rename to accurate functionality "get_child_path"
    def extend_path(
        self, path_extension: str
    ) -> Path:
        return self.__path.extend_path(
            path_extension
        )

    def exists(self) -> bool:
        return self.__path.exists()

    def list_of_components(self):
        return (
            self.__path.list_of_components()
        )

    def item_count(self) -> int:
        return self.__path.item_count()

    def remove_me_from_disk(
        self,
    ) -> None:
        from nf_common_base.b_source.services.file_system_service.objects.files import (
            Files,
        )
        from nf_common_base.b_source.services.file_system_service.objects.folders import (
            Folders,
        )

        if self.exists():
            if isinstance(
                self, Folders
            ):
                # TODO: Path.rmdir() only deletes the folder if empty. shutil.rmtree() deletes the folder and subfolders
                #  regardless it's empty or not - AGREE ONE OPTION
                # self.absolute_path.rmdir()
                shutil.rmtree(
                    path=self.absolute_path,
                    ignore_errors=False,
                )

            elif isinstance(
                self, Files
            ):
                self.absolute_path.unlink()

            else:
                raise TypeError

        else:
            from nf_common_base.b_source.services.reporting_service.reporters.inspection_message_logger import (
                log_inspection_message,
            )

            log_inspection_message(
                message="File system object does not exist on disk: {}".format(
                    self.absolute_path
                ),
                logging_inspection_level_b_enum=LoggingInspectionLevelBEnums.INFO,
            )

    @property
    def drive(self) -> str:
        return self.absolute_path.drive
