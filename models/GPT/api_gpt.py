import os
import openai
import time
import logging
import traceback
from typing import List
from dotenv import load_dotenv
from costs import GPT3
from models.GPT.models import Dialog, Sample, Message, ResultOpenAI
from costs import ModeloGPT
from models.GPT.models import Message, EvalInput, SetEvalDocs, Promt, Sample
import random
from tqdm import tqdm

MAX_TOKENS = 500  # Should be adjust depende on the query
TEMPERATURE = 0.0  # Low temperature to be the more precciss as posible

PARAMS = {'temperature': TEMPERATURE, 'max_tokens': MAX_TOKENS}


class LargeLanguageModel():

    def __init__(self, model: ModeloGPT, **params):
        self.params = params
        self.model = model

        load_dotenv()

        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = os.getenv("OPENAI_API_BASE")
        openai.api_type = 'azure'
        openai.api_version = "2023-05-15"

    def query_openai(self, dialog: Dialog):

        response = openai.ChatCompletion.create(
            engine=self.model.name,
            messages=dialog,
            temperature=self.params['temperature'],
            max_tokens=self.params['max_tokens']
        )

        response_message = response.choices[0]["message"]

        logging.info(response)

        prompt_tokens = response["usage"]["prompt_tokens"]
        promt_price = self.model.price_promt * prompt_tokens / 1000
        completion_price = self.model.price_completion * \
            response["usage"]["completion_tokens"] / 1000
        total_price = promt_price+completion_price
        total_tokens = response["usage"]["total_tokens"]
        logging.info("Coste " + str(total_price) + "$")
        logging.info("Numero de tokens " + str(total_tokens))

        answer = response_message["content"]
        return ResultOpenAI(price_total=total_price, price_input=promt_price, n_tokens_total=total_tokens, n_tokens_input=prompt_tokens, answer=answer)


def generate_dialog(behave: Message, input_task: Message, few_shot_samples: List[Sample] = []) -> Dialog:

    if behave["role"] != "system":
        raise Exception("Bad role, should be system")

    if input_task["role"] != "user":
        raise Exception("Bad role, should be user")

    dialog = [behave]

    for sample in few_shot_samples:
        dialog.append(sample.user)
        dialog.append(sample.agent)

    dialog.append(input_task)

    return dialog


def setup_logging():
    # Configure the log format
    logging.basicConfig(
        # Adjust as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='app.log',  # Log file name
        filemode='a',
        encoding='utf-8'
    )


def log_gpt(model: ModeloGPT, behave: Message, input_task: Message, few_shot_samples: List[Sample] = []) -> ResultOpenAI:

    setup_logging()

    try:

        msgs = generate_dialog(behave, input_task, few_shot_samples)
        result = model.query_openai(msgs)
        logging.info("Answer: " + str(result.model_dump()))
        time.sleep(0.5)

        return result

    except Exception as e:
        print("See log")
        logging.error(str(e))
        logging.error(traceback.format_exc())
        print("Sleeping")
        time.sleep(10)
        return False


def srs(population: list, sample_size: int, seed=8):
    """
    Simple Random Sample
    """
    random.seed(seed)

    sample = random.sample(population, sample_size)

    return sample


def test_bench(lm: LargeLanguageModel, bech: list[Message, EvalInput], samples: list[Sample] = []):
    money = 0
    results = []  # [(y_true, y_pred)]
    # desc="Quering OpenAI"
    for behave, eval in tqdm(bech, desc="Testing bench " + lm.model.name):
        result = log_gpt(lm, behave, eval.input_task, samples)

        if result:  # If dont ERRROR
            results.append([result.answer, eval.y_true])
            money += result.price_total

    return results, money


def eval_pipline(llms: list[LargeLanguageModel], set_evals: list[SetEvalDocs], prompts: list[Promt]):
    pipeline_results = {m.model.name: {c["name"]: {
        p.name: None for p in prompts} for c in set_evals} for m in llms}
    print("Starting test for:", pipeline_results)

    for model in llms:
        model_name = model.model.name
        print("Querying with", model_name)
        for c in set_evals:
            print("Using", c["name"])
            for p in prompts:
                print("With prompt", p.name)

                bench = [({"role": "system", "content": p.behave["content"].replace("{disease}", disease)},
                          EvalInput(input_task=Message(role="user", content=info["text"]), y_true=info["sings"]))
                         for disease, info in c["golds"].items()]

                results, money = test_bench(model, bench, p.samples)
                pipeline_results[model_name][c["name"]][p.name] = {
                    "money": money, "results": results}

    return pipeline_results
