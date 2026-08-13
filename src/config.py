from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PipelineConfig:
    input_path: str = "dbfs:/FileStore/rtcc_transactions"
    checkpoint_path: str = "/tmp/rtcc/checkpoints"
    bronze_table: str = "fraud_db.bronze_transactions"
    silver_table: str = "fraud_db.silver_transactions"
    silver_rejected_table: str = "fraud_db.silver_rejected_transactions"
    gold_features_table: str = "fraud_db.gold_transaction_features"
    gold_alerts_table: str = "fraud_db.gold_high_risk_transactions"
    customer_state_table: str = "fraud_db.gold_customer_behavior_state"
    late_arrivals_table: str = "fraud_db.silver_late_arrivals"
    customer_profile_path: str = "dbfs:/FileStore/customer_profile.csv"
    output_path: str = "dbfs:/FileStore/rtcc_outputs"
    watermark_minutes: int = 120

    @property
    def bronze_checkpoint(self) -> str:
        return f"{self.checkpoint_path}/bronze"

    @property
    def silver_checkpoint(self) -> str:
        return f"{self.checkpoint_path}/silver"

    @property
    def gold_checkpoint(self) -> str:
        return f"{self.checkpoint_path}/gold"

    @property
    def late_checkpoint(self) -> str:
        return f"{self.checkpoint_path}/late"


DEFAULT_CONFIG = PipelineConfig()
