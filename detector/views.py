# views.py
from django import views 
from django.shortcuts import render
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import numpy as np
from .forms import TextInputForm
import unicodedata
import time 
from django.views.generic import (
    CreateView,

)
from .models import Feedback
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin



class AbstractLanguageChecker():
    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

    def check_probabilities(self, in_text, topk=40):
        raise NotImplementedError

    def postprocess(self, token):
        raise NotImplementedError

class LM(AbstractLanguageChecker):
    def __init__(self, model_name_or_path="gpt2"):
        super(LM, self).__init__()
        self.enc = GPT2Tokenizer.from_pretrained('gpt2')
        self.model = GPT2LMHeadModel.from_pretrained("gpt2")
        self.model.to(self.device)
        self.model.eval()
        self.start_token = self.enc(self.enc.bos_token, return_tensors='pt').data['input_ids'][0]
        print("Loaded GPT-2 model from Amazon S3 bucket!")

    def check_probabilities(self, in_text, topk=40):
        # Process input
        token_ids = self.enc(in_text, return_tensors='pt').data['input_ids'][0]
        token_ids = torch.cat([self.start_token, token_ids])
        # Forward through the model
        output = self.model(token_ids.to(self.device))
        all_logits = output.logits[:-1].detach().squeeze()
        # construct target and pred
        # yhat = torch.softmax(logits[0, :-1], dim=-1)
        all_probs = torch.softmax(all_logits, dim=1)

        y = token_ids[1:]
        # Sort the predictions for each timestep
        sorted_preds = torch.argsort(all_probs, dim=1, descending=True).cpu()
        # [(pos, prob), ...]
        real_topk_pos = list(
            [int(np.where(sorted_preds[i] == y[i].item())[0][0])
             for i in range(y.shape[0])])
        real_topk_probs = all_probs[np.arange(
            0, y.shape[0], 1), y].data.cpu().numpy().tolist()
        real_topk_probs = list(map(lambda x: round(x, 5), real_topk_probs))

        real_topk = list(zip(real_topk_pos, real_topk_probs))
        # [str, str, ...]
        bpe_strings = self.enc.convert_ids_to_tokens(token_ids[:])

        bpe_strings = [self.postprocess(s) for s in bpe_strings]

        topk_prob_values, topk_prob_inds = torch.topk(all_probs, k=topk, dim=1)

        pred_topk = [list(zip(self.enc.convert_ids_to_tokens(topk_prob_inds[i]),
                              topk_prob_values[i].data.cpu().numpy().tolist()
                              )) for i in range(y.shape[0])]
        pred_topk = [[(self.postprocess(t[0]), t[1]) for t in pred] for pred in pred_topk]


        # pred_topk = []
        payload = {'bpe_strings': bpe_strings,
                   'real_topk': real_topk,
                   'pred_topk': pred_topk}
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return payload


    def postprocess(self, token):
        with_space = False
        with_break = False
        if token.startswith('Ġ'):
            with_space = True
            token = token[1:]
            # print(token)
        elif token.startswith('â'):
            token = ' '
        elif token.startswith('Ċ'):
            token = ' '
            with_break = True

        token = '-' if token.startswith('â') else token
        token = '“' if token.startswith('ľ') else token
        token = '”' if token.startswith('Ŀ') else token
        token = "'" if token.startswith('Ļ') else token

        if with_space:
            token = '\u0120' + token
        if with_break:
            token = '\u010A' + token

        return token


def humanity_score(final):
    score = (10* final[1]/final[0] + 30 * (final[2]/final[0]) + 100 * (final[3]/final[0]))
    return score 

def main_code(raw_text):
    final = []
    lm = LM()
    payload = lm.check_probabilities(raw_text, topk=5)
    # Print out the number of the different k values  
    final = [len([i for i in payload["real_topk"] if i[0] < 10]),
        len([i for i in payload["real_topk"] if i[0] < 100 and i[0] >= 10]),
        len([i for i in payload["real_topk"] if i[0] < 1000 and i[0] >= 100]),
        len([i for i in payload["real_topk"] if i[0] >= 1000])]
    print(final)
    final = humanity_score(final)
    return final
  

# Input all your text into this. The input() function is not used because it can only take a certain number of words. Also you can put it into hte input string 
# The function cannot take in quotation marks as inputs. So we parse them out with the remove_quotation_marks 


def limit_string_size(string):
    word_list = string.split(" ")
    limited_string = " ".join(word_list[:600])
    print(limited_string)
    return limited_string

from django.shortcuts import render
from .forms import TextInputForm
import PyPDF2
import docx
import magic
import unicodedata
import time

import fitz

def process_file(file):
    file_type = magic.from_buffer(file.read(), mime=True)
    file.seek(0)
    if file_type == 'application/pdf':
        doc = fitz.open(stream=file.read(), filetype='pdf')
        text = ''
        for page in doc:
            text += page.get_text()
        return text
    elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        doc = docx.Document(file)
        text = ''
        for para in doc.paragraphs:
            text += para.text
        return text
    else:
        raise ValueError('Unsupported file type')

# Only signed in users can go onto the detector 
@user_passes_test(lambda u: u.is_authenticated, login_url='/accounts/login/')
def TextInputView(request):
    # Load the user's input 
    form = TextInputForm()
    if request.method == 'POST':
        form = TextInputForm(request.POST, request.FILES)
        if form.is_valid():
            initial = time.time()
            text_input = form.cleaned_data['text_input']
            file_input = form.cleaned_data['file_input']
            # validate the file's content
            if file_input:
                try:
                    input_text = process_file(file_input)
                except ValueError as e:
                    context = {'form': form, 'error': str(e)}
                    return render(request, 'pages/home.html', context)
            else:
                input_text = text_input
            # Limit the word count 
            words = input_text.split()
            limited_words = words[:650]
            input_text = " ".join(limited_words)
            # Write the text after deleting text because it only works this way.
            with open('detector/texts.txt', 'a') as file:
                file.truncate(0)
                file.write(input_text)
            # Cleans the text.
            with open('detector/texts.txt', 'r') as file:
                input_text = file.read()
            # Clean the text form all non-utf shit
            input_text = unicodedata.normalize("NFKD", input_text).encode("ascii", "ignore").decode("utf-8")
            # Run it through the main function; this is where the magic happens
            score = main_code(input_text)
            final = time.time()
            print("Open time:", round(final-initial, 1))
            # Evaluate whether the code was AI or not
            if score > 8.25: 
                decision = "This seems to be human text."
            else: 
                decision = "This text is most likely AI generated."
            context = {'form': form,'output': score, 'score': score, 'decision': decision}
        else:
            context = {'form': form}
    else:
        context = {'form': form}
    
    return render(request, 'pages/home.html', context)

class FeedbackCreateView(CreateView):
    model = Feedback
    fields = ["Name", "Email", "Title", "Content"]
    context_object_name = "Feedback"
    template_name = 'pages/about.html'
    success_url ='/about'