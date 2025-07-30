import pandas as pd

from wbportfolio.models import Fees

from .utils import get_perf_fee_isin

FIELD_MAP = {
    "LastPriceDate": "transaction_date",
    "EndOfDay": "value_date",
    "AccrValueInstrCcy": "total_value",
    "FxRate": "currency_fx_rate",
    "TradingCurrency": "currency__key",
    "#ClientName": "product",
    "InstrumentName": "comment",
}

PERF_FEES_INSTRUMENT_ISIN = "CH0040602242"


def parse(import_source):
    perf_fee_isin = get_perf_fee_isin(import_source.source)
    df = pd.read_csv(import_source.file, encoding="utf-16", delimiter=";")
    df = df.loc[df["ISIN"] == perf_fee_isin, :]
    data = []
    if not df.empty:
        df = df.rename(columns=FIELD_MAP)
        df = df.drop(columns=df.columns.difference(FIELD_MAP.values()))
        df.total_value = -df.total_value
        df["transaction_subtype"] = Fees.Type.MANAGEMENT
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
        df["value_date"] = pd.to_datetime(df["value_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
        df = df.dropna(subset=["product"])
        df.product = df["product"].apply(lambda x: {"identifier": x})
        data = df.to_dict("records")
    return {"data": data}
