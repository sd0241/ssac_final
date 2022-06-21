import torch
from transformers import PreTrainedTokenizerFast
from transformers import BartForConditionalGeneration


class Generate:
    def __init__(self, model_url):
        # self.model = BartForConditionalGeneration.from_pretrained('digit82/kobart-summarization')
        # self.tokenizer = PreTrainedTokenizerFast.from_pretrained('digit82/kobart-summarization')
        # self.device = device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # self.model.to(device)
        self.model = BartForConditionalGeneration.from_pretrained(model_url)
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained(model_url)
        self.device = device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(device)

    def generate_text(self, text):
        with torch.no_grad():
            text = 'summarize :'+text
            text = text.replace('\n', ' ')
            raw_input_ids = self.tokenizer.encode(text)
            input_ids = [self.tokenizer.bos_token_id] + raw_input_ids + [self.tokenizer.eos_token_id]            
            generate = self.model.generate(
                    torch.tensor([input_ids]),  
                    num_beams=4,  
                    max_length=512, 
                    eos_token_id=1)
            gen = self.tokenizer.decode(generate[0],skip_special_tokens=True, clean_up_tokenization_spaces=True)
        return gen 

    def input_generate(self, df, column):
        dataframe = df.copy()
        dataframe['generate_text'] = dataframe['document'].apply(lambda x: self.generate_text(x))
        return dataframe
