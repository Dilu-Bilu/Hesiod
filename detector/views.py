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
import math 
from killgpt.users.models import User

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
    print(final)
    score = (10* final[1]/final[0] + 30 * (final[2]/final[0]) + 115 * (final[3]/final[0]))
    # score = (10* final[1]/final[0] + 50 * (final[2]/final[0]) + 100 * (final[3]/final[0]))
    return score 



def percent_certainty(humanity_score):
    percent = abs(2 / (1 + math.exp(-6 * (humanity_score - 8.25))) - 1)
    lower_range = int(percent * 100) - (int(percent * 100) % 5)
    if lower_range == 100:
        lower_range = 95
    upper_range = lower_range + 5
    
    return f"{lower_range}-{upper_range}"
    
    

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
    elif file_type == 'text/plain':
        # Read and return the contents of a .txt file
        text = file.read().decode('utf-8')
        return text
    else:
        raise ValueError('Unsupported file type')


def count_word_segments(text):
    # Define the list of word segments you want to count # removed iv
    word_segments_to_count = ["zi", "conclusion", "tuna", "gran", "summary", "overall", "tation", "levi", "hema"]
    word_segments_to_count_human = ["aus","involves", "ignoring", "focuses", "substantially", "explores", "ibility","psi", "proposes","departing"]
    # Initialize an empty dictionary to store the word segment counts
    word_segment_count = {segment: 0 for segment in word_segments_to_count}
    word_segment_count_human = {segment: 0 for segment in word_segments_to_count_human}
    # Split the text into words
    words = text.split()
    humanity_score = 0
    # Loop through each word in the text
    for word in words:
        # Remove any punctuation (like periods or commas) from the word
        cleaned_word = word.strip(".,!?").lower()

        # Check if any of the word segments exist within the cleaned word
        for segment in word_segments_to_count:
            if segment in cleaned_word:
                # If it's in the dictionary, add 1 to its count
                word_segment_count[segment] += 1

        for segment in word_segments_to_count_human:
            if segment in cleaned_word:
                # If it's in the dictionary, add 1 to its count
                word_segment_count_human[segment] += 1
    for item in word_segment_count.values():
        humanity_score -= (item) * 0.25
    for item in word_segment_count_human.values():
        humanity_score += (item) * 0.35
    return humanity_score

import openai

def get_feedback(text_input, subject, criteria):
    # Set your OpenAI API key here
    try:
        openai.api_key = "sk-b7vKNqgW4TgBYVcF6V3K3B|bkFJ7jXtZUwq961We57GAs5m"

        prompt = f"propose detailed feedback about the {criteria} for the following {subject} text: {text_input}"
        
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can also try "davinci-codex" for more code-related feedback
            prompt=prompt,
            temperature=0.7,
            max_tokens=150,
            stop=None
        )
        output = response.choices[0].text.strip()
    except: 
        output = """Improving your students' writing skills involves a combination of strategies, practice, and feedback. Here are some ways to help your student improve their writing:

1. **Provide Clear Instructions**: Ensure that your student understands the writing task and any specific requirements or guidelines.

2. **Teach the Writing Process**:
   - **Pre-writing**: Encourage brainstorming, outlining, and organizing ideas before writing.
   - **Drafting**: Emphasize getting thoughts on paper without worrying too much about perfection.
   - **Revising**: Teach the importance of revising for content, clarity, and coherence.
   - **Editing and Proofreading**: Show how to check for grammar, punctuation, and spelling errors.

3. **Offer Feedback**: Provide constructive feedback on their writing, focusing on both strengths and areas for improvement. Encourage them to revise based on your comments.

4. **Read Regularly**: Reading diverse materials, including books, articles, and essays, can improve vocabulary, comprehension, and writing style.

5. **Writing Prompts**: Use writing prompts or creative exercises to stimulate their creativity and writing skills.

6. **Grammar and Style**: Teach grammar rules, sentence structure, and writing style. Encourage them to use varied sentence structures and precise language.

7. **Expand Vocabulary**: Encourage vocabulary development by introducing new words and phrases regularly.

8. **Peer Review**: Have students review and critique each other's work, fostering collaboration and helping them identify common issues.

9. **Provide Examples**: Share well-written essays, stories, or articles as examples to illustrate effective writing.

10. **Encourage Reading Aloud**: Reading their work aloud helps identify awkward phrasing and errors.

11. **Writing Workshops**: Organize writing workshops or writing clubs where students can share and critique each other's work.

12. **Use Technology**: Utilize writing tools or software that highlight grammar and spelling errors.

13. **Set Writing Goals**: Encourage students to set specific, achievable writing goals.

14. **Writing Challenges**: Assign writing challenges or topics that push them out of their comfort zones.

15. **Keep a Journal**: Encourage them to keep a daily journal or diary, which can help improve writing fluency.

16. **Citation and References**: Teach them the importance of proper citation and referencing when using sources.

17. **Practice Regularly**: Writing is a skill that improves with practice. Encourage them to write regularly, even if it's just for personal enjoyment.

18. **Celebrate Achievements**: Acknowledge and celebrate their writing achievements and progress.

19. **Set a Good Example**: Be a model of good writing in your own communication.

20. **Individualized Support**: Recognize that each student may have different needs and areas for improvement. Provide individualized support when necessary.

Remember that improvement takes time, and students may need ongoing support and practice to enhance their writing skills. Provide a nurturing and encouraging environment that fosters creativity and self-expression.
"""
       
    return output 

# Only signed in users can go onto the detector 
# @user_passes_test(lambda u: u.is_authenticated, login_url='/accounts/login/')
def TextInputView(request):
    # Load the user's input 
    user = request.user
    form = TextInputForm()
    if request.method == 'POST':
        form = TextInputForm(request.POST, request.FILES)
        if form.is_valid():
            initial = time.time()
            text_input = form.cleaned_data['text_input']
            file_input = form.cleaned_data['file_input']
            feedback_input = form.cleaned_data['feedback_input']
            subject = form.cleaned_data['grade_level']
            criteria = form.cleaned_data['rubric_field']
            # validate the file's content
            if file_input:
                try:
                    input_text = process_file(file_input)
                except ValueError as e:
                    context = {'form': form, 'error': str(e)}
                    return render(request, 'pages/home.html', context)
            else:
                input_text = text_input
            feedback_words = text_input
            
          
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
            subscore = count_word_segments(input_text)
            score = score + subscore
            # Evaluate whether the code was AI or not and give feedback
            feedback = ''
            if score > 8.25: 
                decision = "This seems to be human text."
                # The Feedback function
            
                if feedback_input == True:
                    user.update_lifetime_assignment_usage()  # Increment lifetime usage
                    user.update_monthly_assignment_usage()  # Update monthly usage
                    user.save()
                    feedback = get_feedback(feedback_words, subject, criteria)
            else: 
                decision = "This text is AI generated."
            percent = percent_certainty(score)
            score = round(score, 2)
            user.update_lifetime_detector_usage()  # Increment lifetime usage
            user.update_monthly_detector_usage()  # Update monthly usage
            user.save()
            context = {'form': form, 'percent': percent , 'output': score, 'score': score, 'decision': decision, 'input_text': input_text, 'feedback': feedback}
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