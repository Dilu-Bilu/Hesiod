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
from assignment.models import Assignment
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
    word_segments_to_count = ["iv", "zi", "conclusion", "tuna", "gran", "summary", "overall", "tation", "levi", "hema"]
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

from openai import OpenAI
import re
from config.settings.base import OPEN_AI_KEY
def get_feedback(total_marks, assignment_prompt, rubric_criteria, student_writing):
    
    client = OpenAI(api_key=OPEN_AI_KEY)
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
    {"role": "system", "content": "You are a teaching assistant, skilled in marking your student's english/history writings with brutal honesty white giving them feedback of how they can improve their writing in each criteria through using examples from their writing and showing how they can be improved. Also you mark very moderately and are a fair marker, who does not give students a hard time."},
    {"role": "user", "content": f"""Task: Evaluate a student's writing based on an assignment prompt, rubric criteria, and provide constructive feedback with overall advice and direct sentence examples of how improvements cuold be made by using example sentences inside the student's work. 

        Assignment Marks: 
        This is the amount of marks the assignment is out of, represented as (yourmarks)/{total_marks}
        
        Assignment Marks: {total_marks}    

        Assignment Prompt:
        Please replace the following section with the assignment prompt for this evaluation. Describe the assignment topic, requirements, and any specific guidelines for the student's writing. Ensure it is clear and comprehensive.

        Assignment Prompt: {assignment_prompt}

        Rubric Criteria:
        Replace the following section with the rubric criteria to be used for assessing the student's writing. Include criteria descriptions, point allocations, and the total marks possible. Ensure each criterion is distinct and understandable.

        Rubric Criteria: {rubric_criteria}

        Student's Writing:
        Replace the subsequent section with the actual content of the student's writing. Ensure it aligns with the assignment prompt and will be used for assessment based on the provided rubric.

        Student's Writing: {student_writing}

        Expected Output:

        Marks: The response should include the total marks attained out of the total marks available.
        Criterion Feedback: Feedback for each individual criterion outlined in the rubric. This should encompass strengths, areas for improvement, and specific comments based on the student's writing.
        General Advice: Provide overall advice for the student's improvement, supported by quoted examples from their writing. Identify common issues or patterns observed and suggest ways to enhance the quality of their writing.
        Please ensure the output is presented in a structured and readable format, allowing easy parsing of the marks, feedback, and general advice for further analysis and understanding.
        """}
        ]
        )

    response = completion.choices[0].message
    txt = response.content
    print(txt)

    # Extract marks
    marks = re.search(r"(\d+/\d+)", txt)
    if marks:
        marks = marks.group(1)  # Extract only the matched marks
    else:
        marks = None

    # Extract feedback
    feedback = re.findall(r"Criterion Feedback:(.+?)General Advice:", txt, re.DOTALL)
    if feedback:
        feedback = feedback[0]
    else:
        feedback = None

    # Extract general advice
    gen_advice = re.findall(r"General Advice:(.*)", txt, re.DOTALL)
    if gen_advice:
        gen_advice = gen_advice[0]
    else:
        gen_advice = None
    if marks is not None:
        marks_display = marks.split('/')
        top = int(marks_display[0])
        bot = int(marks_display[1])
        display_mark = 100 * (top/bot)
    else:
        # Handle the case where marks is None
        display_mark = 0  # or any other default value or logic
   
    return marks, feedback, gen_advice, display_mark

# Only signed in users can go onto the detector 
# @user_passes_test(lambda u: u.is_authenticated, login_url='/accounts/login/')
def TextInputView(request):
     # Retrieve the user object from the request or context
    user = request.user if request.user.is_authenticated else None
    if request.method == 'POST':
        form = TextInputForm(user, request.POST, request.FILES)
        if form.is_valid():
            initial = time.time()
            text_input = form.cleaned_data['text_input']
            file_input = form.cleaned_data['file_input']
            feedback_input = form.cleaned_data['feedback_input']
            
            # Accessing the feedback_choice value from the submitted form
            feedback_choice = form.cleaned_data['feedback_choice']
            
            try:
                # Get the Feedback object based on the selected feedback_choice (assuming Feedback is related to the Assignment model)
                feedback = Assignment.objects.get(pk=feedback_choice)
                #total_marks, assignment_prompt, rubric_criteria, student_writing
                total_marks = feedback.total_marks
                assignment_prompt = feedback.assignment_description
                rubric_criteria = feedback.assignment_criteria
            except:
                total_marks = 0
                assignment_prompt = ""
                rubric_criteria = ""
            

            # validate the file's content
            if file_input:
                try:
                    input_text = process_file(file_input)
                except ValueError as e:
                    context = {'form': form, 'error': str(e)}
                    return render(request, 'pages/home.html', context)
            else:
                input_text = text_input
           
            
            student_writing = input_text
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
                    marks, feedback, gen_advice, display_mark = get_feedback(total_marks, assignment_prompt, rubric_criteria, student_writing)
            else: 
                decision = "This text is AI generated."
            percent = percent_certainty(score)
            score = round(score, 2)
            user.update_lifetime_detector_usage()  # Increment lifetime usage
            user.update_monthly_detector_usage()  # Update monthly usage
            user.save()
            if feedback_input == True and (score > 8.25):
                context = {'form': form, 'percent': percent , 'output': score, 'score': score, 'decision': decision, 'input_text': input_text, 'marks': marks, 'gen_advice': gen_advice, 'feedback': feedback, 'display_mark': display_mark}
            else:
                context = {'form': form, 'percent': percent , 'output': score, 'score': score, 'decision': decision, 'input_text': input_text,}
        else:
            context = {'form': form}
    else:
        form = TextInputForm(user)
        context = {'form': form}
    
    return render(request, 'pages/home.html', context)

class FeedbackCreateView(CreateView):
    model = Feedback
    fields = ["Name", "Email", "Title", "Content"]
    context_object_name = "Feedback"
    template_name = 'pages/about.html'
    success_url ='/about'