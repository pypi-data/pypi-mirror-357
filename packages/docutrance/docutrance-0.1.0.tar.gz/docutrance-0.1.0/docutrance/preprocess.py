import json
import os
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import spacy_udpipe
import torch
import tqdm as tqdm

class UDSentenceTokenizer:
    """
    Manages and caches multiple UDPipe-based spaCy tokenizers for multilingual processing.

    This class allows efficient switching between tokenizers for different languages
    by preloading them into memory. It is particularly useful when working with
    multilingual datasets where sentence segmentation or tokenization is needed
    in multiple languages.

    Parameters:
        languages (list of str): List of ISO 639-1/2 language codes supported by spacy-udpipe.
                                 Each model will be downloaded (if not already present) and loaded.

    Example:
        manager = UDTokenizerManager(['en', 'fr', 'de'])
        sentences = manager.tokenize('fr', "Bonjour. Comment ça va ?")

    Methods:
        tokenize(lang, text):
            Tokenizes and segments the given text into sentences using the language-specific model.
            Returns a list of sentence strings.
    """
    def __init__(self, languages):
        self.models = {}
        print(f"Initializing UD Tokenizer for {languages}. . .")
        for lang in languages:
            spacy_udpipe.download(lang)  
            self.models[lang] = spacy_udpipe.load(lang)
    
    def tokenize(self, lang, text):
        """
        Tokenizes and segments the input text using the tokenizer for the specified language.

        Parameters:
            lang (str): The language code (e.g., 'en', 'fr') corresponding to the desired tokenizer.
            text (str): The text to be tokenized and segmented into sentences.

        Returns:
            list of str: A list of sentences as segmented by the language model.

        Raises:
            ValueError: If the specified language model is not loaded.
        """
        nlp = self.models.get(lang)
        if not nlp:
            raise ValueError(f"Language model for '{lang}' not loaded.")
        return [sent.text for sent in nlp(text).sents]

def align_sentences(
    source_sentences: list[str],
    target_sentences: list[str],
    model: SentenceTransformer
) -> dict:
    """
    Align source and target sentences using sentence embeddings and cosine similarity.
    """

    embed = lambda sentences: model.encode(sentences, convert_to_tensor=True)
    source_embeddings = embed(source_sentences)
    target_embeddings = embed(target_sentences)

    # Compute cosine similarity matrix
    similarity_matrix = cos_sim(source_embeddings, target_embeddings)

    best_matches = []
    best_scores = []

    for _, row in enumerate(similarity_matrix):
        best_match_idx = row.argmax().item()
        best_score = row[best_match_idx].item()
        best_matches.append(target_sentences[best_match_idx])
        best_scores.append(best_score)

    return {
        "source": source_sentences,
        "target": best_matches,
        "score": best_scores
    }

def align_sentences_process(
    io_paths: dict[str],  # Required keys: 'corpus', 'output'
    model: SentenceTransformer,
    source_language: tuple = ('en', 'english'),
    target_languages: list = ['es', 'fr', 'it', 'pt']
):
    """
    Aligns sentences from a parallel corpus using multilingual sentence embeddings.

    This function compares source-language sentences with multiple target-language sentences
    and produces sentence-level alignments based on cosine similarity.

    Parameters:
        io_paths (dict): A dictionary with the following keys:
            - "corpus": Path to the input JSON corpus file.
            - "output": Path to the final `.parquet` file where the combined alignment results will be saved.

        model (SentenceTransformer): A pre-loaded SentenceTransformer model used to compute embeddings.

        source_language (tuple): A tuple defining the source language.
            - The first element is the language code (e.g., 'en').
            - The second element is the name to use in the output table (e.g., 'english').

        target_languages (list of str): A list of language codes for the target languages to be processed.

    Output:
        - Saves intermediate `.parquet` files: one per (section, target language) pair.
        - Merges all intermediate files into a single `.parquet` file saved at the specified output path.
    """
    source, name = source_language
    tokenizer = UDSentenceTokenizer([source] + target_languages)

    # Step 1: Prepare output paths
    io_paths["intermediate"] = Path.cwd() / "intermediate"
    os.makedirs(io_paths["intermediate"], exist_ok=True)
    io_paths["files"] = []


    # Step 2: Load corpus JSON into dictionary
    corpus = json.loads(Path(io_paths["corpus"]).read_text(encoding='utf-8'))

    # Step 3: Iterate over each section in the corpus
    for section_id, entry in corpus.items():
        tokenize = lambda lang: tokenizer.tokenize(lang, entry[lang]["content"])

        sentences = {"source": tokenize(source)}
        headers = {"source": entry[source]["header"]}

        for target in [lang for lang in target_languages if lang in entry.keys()]:

            # Step 4a: Check if the section, language pair has already been processed
            output_path = Path(io_paths["intermediate"]) / f"{section_id}-{source}-{target}.parquet"
            io_paths["files"].append(output_path)
            if output_path.exists():
                print(f"Section {section_id}, {source}-{target} is already finished. Continuing. . . ")
                continue

            print(f"Processing Section {section_id}, {source}-{target}. . . ")

            # Step 4b: Extract, tokenize, and embed English and non-English content
            sentences.update({"target": tokenize(target)})
            headers.update({"target": entry[target]["header"]})

            result = align_sentences(sentences["source"], sentences["target"], model)

            # Step 4e: Build and save alignment results as a parquet file
            output = pd.DataFrame({
                "section_id": section_id,
                "target_language": target,
                f"{name}_header": headers["source"],
                f"{name}_sentence": result["source"],
                f"non_{name}_header": headers["target"],
                f"non_{name}_sentence": result["target"],
                "similarity_score": result["score"]
            })

            output.to_parquet(output_path)

    # Step 5: Merge all intermediate parquet files into final output
    final_output = pd.concat(
        [pd.read_parquet(file) for file in io_paths["files"]]
    ).reset_index(drop=True)
    os.makedirs(os.path.dirname(io_paths["output"]), exist_ok=True)
    final_output.to_parquet(io_paths["output"])
    print(f"Combined intermediate outputs. Saved to {io_paths['output']}")
    