#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import fitz
import docx2txt
import firebase_admin
from firebase_admin import credentials, firestore, storage

#firebase_admin initialization
cred = credentials.Certificate('./interview_project_service_key.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'interview-project-3098c.appspot.com'})


# In[2]:


firestore_db = firestore.client()
bucket = storage.bucket()
prefix = 'resumes/'
location= './'
jobD = 'jobDescription/'
jdName = 'jobdescription.docx'
jobDesc = jobD + jdName

### JOB DESCRIPTION ###

blob = bucket.get_blob(jobDesc)
# print(blob.name)
blob.download_to_filename(jdName)
jd = docx2txt.process(jdName)
# print (jd)
path = os.path.join(location, jdName)
os.remove(path)
# print("%s has been removed successfully" %jdName)

# get the resume and JD from storage 
### RESUME ###

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
blobs = bucket.list_blobs(prefix=prefix)
for blob in blobs:
    if blob.name == prefix:
        print ('Welcome!')
    else:
        location= './'
        resume_name = remove_prefix(blob.name, prefix)
        print("Reading " + resume_name + ' ....')
        blob = bucket.get_blob(blob.name)
        blob.download_to_filename(resume_name)
#         print (resume_name)
        
        if resume_name.endswith(".docx"):
            res = docx2txt.process(resume_name)
        #     print(res)
        elif resume_name.endswith(".pdf"):
            with fitz.open(resume_name) as doc:
                res = ""
                for page in doc:
                    res += page.getText()
#             print(res)
#             doc.close()
        #     print(res)
        path = os.path.join(location, resume_name)
#         os.remove(path)
        print("%s has been removed successfully" %resume_name)

        text =[res, jd]
        from sklearn.feature_extraction.text import CountVectorizer
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(text)

        from sklearn.metrics.pairwise import cosine_similarity
        # print("\nSimilarity Scores: ")
        # print(cosine_similarity(count_matrix))

        percent = cosine_similarity(count_matrix)[0][1] * 100
        percent = round(percent, 2) 
        print('Your Resume ' + resume_name +' matches about '+ str(percent) + '%of the Job Description:'+ jdName ) 

        if percent > 75.00:
            print('resume verified \n\n')
        else:
            print('resume not verified \n\n')
#after comparing Resume and JD  details of user and score gets added in firestore
        user_id = "9876"
        user_name = resume_name
        location = "Pune"
        applied_JD = jdName
        number = "1234566"
        firestore_db = firestore.client()
        firestore_db.collection(u'Resume Screener').document(user_id).set
        ({'user_name':user_name ,'location':location,'applied_JD':applied_JD,'Phone_number':number, 'Percent Matching':percent})






