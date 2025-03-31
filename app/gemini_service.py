import os
import json
import google.generativeai as genai
from config.settings import get_config
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.web import SimpleWebPageReader
from llama_index.readers.file import ImageReader

# docx_file_path = "./data/training/document.docx"
json_paths = ["./data/training/question.json", "./data/training/FAQ_output_fixed.json"]
web_urls = [
    "https://www.kku.ac.th",
    "https://www.en.kku.ac.th/web/%E0%B8%87%E0%B8%B2%E0%B8%99%E0%B8%9A%E0%B8%A3%E0%B8%B4%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%A7%E0%B8%B4%E0%B8%8A%E0%B8%B2%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%81%E0%B8%A5%E0%B8%B0%E0%B8%A7%E0%B8%B4%E0%B8%88/#1523875822874-a039c957-3a3f"
]
image_paths = [
    "./data/examples/385541682_293500413465859_643983524389644808_n.jpg", "./data/examples/ค่าธรรมเนียมการศึกษาป.ตรี-650x900.png"
]

class GeminiService:
    def __init__(self, json_paths=json_paths, image_dir=image_paths, web_urls=web_urls):
        self.config = get_config()
        self.api_key = self.config.GOOGLE_AI_API_KEY
        self.model_name = self.config.GEMINI_MODEL_NAME
        self.json_paths = json_paths if json_paths else ["./data/training/question.json"]
        self.image_dir = image_dir
        self.web_urls = web_urls if web_urls else []

        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY not set in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def get_json_data(self):
        combined_data = {}
        for path in self.json_paths:
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    json_data = json.load(file)
                    combined_data.update(json_data)
            except Exception as e:
                print(f"Error reading JSON file {path}: {str(e)}")
        return json.dumps(combined_data, ensure_ascii=False)
    
    def get_image_data(self):
            if not self.image_dir:
                return ""
            
            image_reader = ImageReader()
            image_texts = []
            
            for img_path in self.image_dir:
                try:
                    image_docs = image_reader.load_data(file=img_path)
                    for doc in image_docs:
                        image_texts.append(doc.text)
                except Exception as e:
                    print(f"Error reading image {img_path}: {str(e)}")
            
            return "\n".join(image_texts)
    
    def get_web_data(self):
        if not self.web_urls:
            return ""
        
        web_reader = SimpleWebPageReader()
        web_texts = []
        
        try:
            web_docs = web_reader.load_data(urls=self.web_urls)
            for doc in web_docs:
                web_texts.append(doc.text)
        except Exception as e:
            print(f"Error reading web data: {str(e)}")
        
        return "\n".join(web_texts)



    def generate_with_rag(self, query, temperature=0.7):
        """สร้างคำตอบโดยใช้ข้อมูลจากไฟล์ JSON, DOCX และ URL"""
        json_data = self.get_json_data()
        image_data = self.get_image_data()
        web_data = self.get_web_data()
        
        system_prompt = """You are the KKU Information AI. You have access to a JSON file, a DOCX document, and a web URL containing detailed and up-to-date information about Khon Kaen University (KKU). Your task is to answer any user query using only the data provided in these sources. **However, if the queried information is not found in these sources, you must search for the information from reliable sources to answer the question.** Before providing your answer, verify the credibility of the information by checking if multiple reputable sites refer to it. Do not provide random or inaccurate answers. If the search does not yield any results or the information is unavailable in your model, clearly respond that the information is unavailable.
        You must always provide your answers in both Thai and English. Ensure that your responses are precise, fact-based, and directly address the user's question. Do not include any extraneous information beyond what is necessary to answer the query.
        If you don't know just say you don't know don't try to much to generate false information. 
        For example:
        User Query: Where are EN16101?
        Your Response:
        ภาษาไทย: อยู่ข้างตึก 50
        English: Near 50th anniversary building

        Important rules:
        1. Always use the data from the JSON file, DOCX document, and web URL to answer the question, if the information is available there.
        2. **If the required information is not found in these sources, search for the information from reliable sources.**
        3. Before answering, verify the credibility of the information by checking if multiple reputable sites confirm it.
        4. Do not provide random or inaccurate information.
        5. If the search does not yield any results or the information is unavailable, clearly state that the information is unavailable.
        6. Keep the response strictly limited to answering the user's query without additional commentary or unrelated details.
        7. Answer only in 1 languages (Thai or English) if user ask in thai answer in thai if english answer in english.
        8. Must answer with raw text, do not include any HTML tags or formatting.
        9. Use bold text for important information or proper names, such as 'วิศวกรรมโทรคมนาคม', Faculty of Engineering, or EN16101, to make key details stand out.
        10. If the response consists of multiple points, ensure proper spacing and formatting for readability, using line breaks and indentation where necessary.
        """

        prompt = (f"{system_prompt}\n\n"
                  f"JSON Data:\n{json_data}\n\n"
                  f"Extracted Image Text:\n{image_data}\n\n"
                  f"Extracted Web Text:\n{web_data}\n\n"
                  f"User Query:\n{query}\n\nResponse:")
        
        try:
            response = self.model.generate_content(prompt, generation_config={"temperature": temperature})
            return {"success": True, "response": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
        