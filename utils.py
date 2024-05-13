import json
import pickle
import csv
import os
import pandas as pd
from typing import List, Literal, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel


Role = Literal["user", "assistant", "system"]

class Message(TypedDict):
    role: Role
    content: str
    
class Sample(BaseModel):
    user: Message
    agent: Message

class SetEvalDocs(TypedDict):
    name: str
    docs: List
    
class Promt(BaseModel):
    behave: Message
    name: str
    samples: Optional[list[Sample]] = []
    
    
def filter_gold_items(golds, sample_index):
  """
  Filters the gold items dictionary based on the provided indices.

  Args:
      golds: A dictionary containing gold items.
      examples_indices: A list of indices specifying items to exclude.

  Returns:
      A new dictionary containing only the non-selected gold items.
  """

  gold_items_copy = dict(golds) 

  for index in sample_index: 
    del gold_items_copy[list(gold_items_copy.keys())[index]]  # Remove item by index from copy

  return gold_items_copy


def samples_selection(golds, sample_index):
    golds_items = list(golds.items())
    items_selec = [golds_items[i] for i in sample_index]

    texts = []
    symptoms_lists = []

    for index, item in enumerate(items_selec):
        text = item[1]['text']
        symptoms = item[1]['sings']
        symptoms_string = '#'.join(symptoms)

        texts.append(text)
        symptoms_lists.append(symptoms_string)

    return texts, symptoms_lists, filter_gold_items(golds_items, sample_index)

def load_golds(path):
    golds = []

    with open(path) as f:
        golds = json.load(f)

    print("Number of Diseases: ", len(golds))

    return golds


def load_results(path:str):
    results = None
    with open(path) as f:
        results = json.load(f)

    return results
def dump_results(results, path):
    with open(path, 'w') as archivo:
        json.dump(results, archivo, indent=2)


def dump_cache(cuis_tuis, path:str):
    with open(path, 'wb') as f:
        pickle.dump(cuis_tuis, f)

def load_cache(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)

    return data


class BasePromt(BaseModel):
    id: int
    msg: str
    description: str
    n_tokens:int

def load_promts(path: str) -> List[BasePromt]:

    df = pd.read_excel(path)

    dict_prompts = {
        row.id: BasePromt(
            id=row.id,
            description=row.description,
            msg=row.prompt,
            n_tokens=len(row.prompt.split())
        )
        for row in df.itertuples(index=False)
    }
    
    return dict_prompts

class GPTPromt(BaseModel):
    id: int
    msg: Message
    description: str
    n_tokens:int

def load_promts_GPT(path: str) -> List[GPTPromt]:

    df = pd.read_excel(path)

    dict_prompts = {
        row.id: GPTPromt(
            id=row.id,
            description=row.description,
            msg=Message(role="system", content=row.prompt),
            n_tokens=len(row.prompt.split())
        )
        for row in df.itertuples(index=False)
    }
    
    return dict_prompts

def get_tui_columns(csv_file_path, columns='both'):
    """
    Arguments:
    csv_file_path (str): Full path of the CSV file containing TUI information.
    columns (str): Specify which column(s) to return. Possible values are 'name', 'definition', or 'both'. Default is 'both'.
    
    """
    if columns not in ['name', 'definition', 'both']:
        raise ValueError("Invalid value for 'columns'. Use 'name', 'definition', or 'both'.")

    names = []
    definitions = []

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if columns == 'name' or columns == 'both':
                names.append(row['Name'])
            if columns == 'definition' or columns == 'both':
                definitions.append(row['Definition'])

    if columns == 'name':
        return ', '.join(names)
    elif columns == 'definition':
        return ', '.join(definitions)
    else:
        combined = [f"{name}: {definition}" for name, definition in zip(names, definitions)]
        return ', '.join(combined)

def load_samples(csv_file):
    """
    Load samples from a CSV file into lists.

    Arguments:
    csv_file (str): Path to the CSV file.

    Returns:
    list: List of text samples.
    list: List of gold formatted samples.
    """
    samples = []

    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)  # Skip the header row if exists
        for row in reader:
            text = row[0]
            gold = row[1]
            samples.append({"role": "user", "content": text})
            samples.append({"role": "assistant", "content": gold })

    return samples

def load_samples_text(csv_file):
    """
    Load samples from a CSV file into lists.

    Arguments:
    csv_file (str): Path to the CSV file.

    Returns:
    list: List of text samples.
    list: List of gold formatted samples.
    """
    samples = []

    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)  # Skip the header row if exists
        for row in reader:
            text = row[0]
            gold = row[1]
            samples.append(text)
            samples.append(gold)

    return samples


