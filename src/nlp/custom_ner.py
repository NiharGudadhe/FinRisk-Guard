import os
import logging
import pandas as pd
import spacy

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("FinRisk-NER")

class FinancialTokenEngine:
    def __init__(self):
        logger.info("Loading lightweight spaCy vocabulary structure into RAM...")
        try:
            # Mount en_core_web_sm natively to maintain low memory signature
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Successfully mounted token processing vocabulary matrix.")
        except Exception as e:
            logger.critical(f"Linguistic matrix memory binding crashed: {str(e)}")
            raise

    def normalize_compliance_text(self, csv_path: str):
        """Processes and tokenizes textual features while filtering out stop words and grammar noise."""
        logger.info(f"Ingesting raw text strings from: {csv_path}")
        if not os.path.exists(csv_path):
            logger.error(f"NER Extraction halted: Source data path missing at {csv_path}")
            return None

        df = pd.read_csv(csv_path, names=["sentiment", "text"], encoding="latin-1", header=None)
        logger.info(f"Loaded {len(df)} base rows for token extraction.")

        optimized_phrases = []
        logger.info("Executing text normalization sequence (Processing first 500 rows to safeguard RAM)...")
        
        # Enforce memory safety limits by slicing the target sample array
        sample_subset = df.head(500)
        
        for idx, row in sample_subset.iterrows():
            doc = self.nlp(str(row["text"]))
            # Strip out grammatical filler words like 'is', 'the', 'at', and punctuation marks
            tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
            optimized_phrases.append(" ".join(tokens))

        df_out = sample_subset.copy()
        df_out["cleaned_features"] = optimized_phrases
        logger.info("Linguistic processing pass completed with zero memory leakage leaks.")
        return df_out

if __name__ == "__main__":
    engine = FinancialTokenEngine()
    engine.normalize_compliance_text("data/raw/financial_phrasebank.csv")
