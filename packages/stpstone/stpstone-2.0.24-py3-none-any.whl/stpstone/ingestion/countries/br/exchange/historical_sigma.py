import pandas as pd
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from logging import Logger
from requests import Response
from time import sleep
from stpstone._config.global_slots import YAML_B3_HISTORICAL_SIGMA
from stpstone.utils.cals.handling_dates import DatesBR
from stpstone.utils.connections.netops.proxies.managers.free import YieldFreeProxy
from stpstone.ingestion.abc.requests import ABCRequests
from stpstone.utils.parsers.dicts import HandlingDicts


class HistoricalSigmaB3(ABCRequests):

    def __init__(
        self,
        session: Optional[Session] = None,
        dt_ref:datetime=DatesBR().sub_working_days(DatesBR().curr_date, 1),
        cls_db:Optional[Session]=None,
        logger:Optional[Logger]=None,
        token:Optional[str]=None,
        list_slugs:Optional[List[str]]=None
    ) -> None:
        super().__init__(
            dict_metadata=YAML_B3_HISTORICAL_SIGMA,
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
        self.token = token,
        self.list_slugs = list_slugs

    def req_trt_injection(self, resp_req:Response) -> Optional[pd.DataFrame]:
        json_ = resp_req.json()
        df_ = pd.DataFrame(
            HandlingDicts().add_key_value_to_dicts(
                json_['results'],
                [json_['page']]
            )
        )
        return df_

    @property
    def composition(self) -> pd.DataFrame:
        list_ser = list()
        for i in range(1, 4):
            list_ser.extend(
                self.source(f'group_{i}', bl_fetch=True)\
                    .to_dict(orient='records')
            )
        return pd.DataFrame(list_ser)
