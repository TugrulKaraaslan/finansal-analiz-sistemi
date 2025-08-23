from __future__ import annotations
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, ValidationError
import os, json


# --- Ortak yardımcılar ---


def _must_exist(p: Path) -> Path:
    if not p.exists():
        raise ValueError(f"path not found: {p}")
    return p


# --- Colab/ana konfig ---


class ColabData(BaseModel):
    excel_dir: Path = Field(..., description="Excel dosyalarının bulunduğu dizin")

    @field_validator('excel_dir', mode='before')
    @classmethod
    def _norm_excel(cls, v):
        return Path(str(v)).expanduser().resolve()

    @field_validator('excel_dir')
    @classmethod
    def _exists_excel(cls, v: Path):
        return _must_exist(v)


class ColabConfig(BaseModel):
    data: ColabData

    @classmethod
    def from_yaml_with_env(cls, yaml_path: Path) -> 'ColabConfig':
        import yaml

        raw = yaml.safe_load(Path(yaml_path).read_text())
        # ENV override (isteğe bağlı)
        excel_env = os.getenv('EXCEL_DIR')
        if excel_env:
            raw.setdefault('data', {})['excel_dir'] = excel_env
        return cls(**raw)


# --- Costs ---


class CostsCommission(BaseModel):
    model: Literal['fixed_bps', 'per_share_flat', 'none'] = 'fixed_bps'
    bps: float = 5.0
    min_cash: float = 0.0


class CostsTaxes(BaseModel):
    bps: float = 0.0


class CostsSpread(BaseModel):
    model: Literal['half_spread', 'fixed_bps', 'none'] = 'half_spread'
    default_spread_bps: float = 7.0


class CostsSlippage(BaseModel):
    model: Literal['atr_linear', 'fixed_bps', 'none'] = 'atr_linear'
    bps_per_1x_atr: float = 10.0


class CostsApply(BaseModel):
    price_col: str = 'fill_price'
    qty_col: str = 'quantity'
    side_col: str = 'side'
    date_col: str = 'date'
    id_col: str = 'trade_id'


class CostsReport(BaseModel):
    write_breakdown: bool = True
    output_dir: Path = Path('artifacts/costs')

    @field_validator('output_dir', mode='before')
    @classmethod
    def _norm(cls, v):
        return Path(str(v)).expanduser().resolve()


class CostsConfig(BaseModel):
    enabled: bool = True
    currency: str = 'TRY'
    rounding_cash_decimals: int = 2
    commission: CostsCommission = CostsCommission()
    taxes: CostsTaxes = CostsTaxes()
    spread: CostsSpread = CostsSpread()
    slippage: CostsSlippage = CostsSlippage()
    apply: CostsApply = CostsApply()
    report: CostsReport = CostsReport()


# --- Portfolio ---


class Sizing(BaseModel):
    mode: Literal['risk_per_trade', 'fixed_fraction', 'target_weight'] = 'risk_per_trade'
    risk_per_trade_bps: float = 50.0
    stop_model: Literal['atr_multiple', 'percent'] = 'atr_multiple'
    atr_period: int = 14
    atr_mult: float = 2.0
    fixed_fraction: float = 0.1


class Constraints(BaseModel):
    max_positions: int = 10
    max_position_pct: float = 0.2
    max_gross_exposure: float = 1.0
    allow_short: bool = False
    lot_size: int = 1
    min_qty: int = 1
    round_qty: Literal['floor', 'round', 'ceil'] = 'floor'


class Pricing(BaseModel):
    execution_price: Literal['close', 'open', 'custom_column'] = 'close'
    price_col: str = 'close'


class PortfolioReport(BaseModel):
    output_dir: Path = Path('artifacts/portfolio')
    write_trades: bool = True
    write_daily: bool = True

    @field_validator('output_dir', mode='before')
    @classmethod
    def _norm(cls, v):
        return Path(str(v)).expanduser().resolve()


class PortfolioConfig(BaseModel):
    enabled: bool = True
    base_currency: str = 'TRY'
    initial_equity: float = 1_000_000
    sizing: Sizing = Sizing()
    constraints: Constraints = Constraints()
    pricing: Pricing = Pricing()
    report: PortfolioReport = PortfolioReport()


# --- JSON Schema export ---


def export_json_schema(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'colab_config.schema.json').write_text(
        json.dumps(ColabConfig.model_json_schema(), indent=2), encoding='utf-8'
    )
    (out_dir / 'costs.schema.json').write_text(
        json.dumps(CostsConfig.model_json_schema(), indent=2), encoding='utf-8'
    )
    (out_dir / 'portfolio.schema.json').write_text(
        json.dumps(PortfolioConfig.model_json_schema(), indent=2), encoding='utf-8'
    )

