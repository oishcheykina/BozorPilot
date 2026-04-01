class SoliqClassifierService:
    """
    Placeholder integration layer for future official classifier/category syncing.
    Replace mock responses with live Soliq or tax-classifier data mapping later.
    """

    def fetch_categories(self):
        return [
            {"external_code": "ELEC-SMART", "name": "Smartphones"},
            {"external_code": "ELEC-HOME", "name": "Household Electronics"},
            {"external_code": "HOME-ESS", "name": "Household Goods"},
        ]
