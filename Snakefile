rule prepare_temperature_data:
    input:
        raw="data/raw/vienna_hohe_warte_tlmax.csv"
    output:
        clean="data/processed/vienna_hohe_warte_tlmax.csv"
    shell:
        """
        python scripts/prepare_data.py \
          --input {input.raw} \
          --output {output.clean}
        """
