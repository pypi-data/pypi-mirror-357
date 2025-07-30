from nf_common_base.b_source.services.logging_service.logging_library_extentions.picologging.flat.loggers.picologging_flat_loggers import (
    PicologgingFlatLoggers,
)


class FlatLoggerFacade:
    __logger = PicologgingFlatLoggers(
        "picologging_flat_logger"
    )

    @classmethod
    def log(
        cls,
        message: str,
        is_headers: bool = False,
    ) -> None:
        cls.__logger.log_flat(
            message=message,
            is_headers=is_headers,
        )
