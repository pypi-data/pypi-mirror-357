import pandas as pd
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from logging import Logger
from requests import Response
from time import sleep
from stpstone._config.global_slots import YAML_OLINDA_BCB
from stpstone.utils.cals.handling_dates import DatesBR
from stpstone.ingestion.abc.requests import ABCRequests


class OlindaBCB(ABCRequests):

    def __init__(
        self,
        session: Optional[Session] = None,
        dt_start: datetime = DatesBR().sub_working_days(DatesBR().curr_date, 60),
        dt_end: datetime = DatesBR().sub_working_days(DatesBR().curr_date, 1),
        dt_ref: datetime = DatesBR().sub_working_days(DatesBR().curr_date, 1),
        cls_db: Optional[Session] = None,
        logger: Optional[Logger] = None,
        token: Optional[str] = None,
        list_slugs: Optional[List[str]] = None
    ) -> None:
        super().__init__(
            dict_metadata=YAML_OLINDA_BCB,
            session=session,
            dt_ref=dt_ref,
            cls_db=cls_db,
            logger=logger,
            token=token,
            list_slugs=list_slugs
        )
        self.session = session
        self.dt_ref = dt_ref
        self.cls_db = cls_db
        self.logger = logger
        self.list_slugs = list_slugs
        self.dt_start = dt_start
        self.dt_end = dt_end
        self.dt_start_repr = dt_start.strftime('%m-%d-%Y')
        self.dt_end_repr = dt_end.strftime('%m-%d-%Y')

    def req_trt_injection(self, resp_req: Response) -> Optional[pd.DataFrame]:
        return pd.DataFrame(resp_req.json()["value"])
