import json
import sys
import os
import re
import time

from storybuilder import Story, CosUploader, VoiceSynthesizer

VOICE_BREAK_TAG="<break time=\"1500ms\"/>"

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

CONCENTRAK_PLACEHOLDER = "\u200b\n"

def remove_emojis(text):
    emojiPattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U0001F926-\U0001F991"
                    "]+", flags = re.UNICODE)
    return re.sub(emojiPattern, '', text)

def has_chinese_char(text):
  """Checks if a string contains at least one Chinese character.

  Args:
      text: The string to be checked.

  Returns:
      True if the string contains at least one Chinese character, False otherwise.
  """
  # Check if any character in the string falls within the Unicode range of Chinese characters
  return any(u'\u4e00' <= char <= u'\u9fff' for char in text)

# Adjustment on concentrak title for better positioning of English only content
def concentrak_treatment(inputStr):
    if len(inputStr.split("\n\n")) > 1:
        return CONCENTRAK_PLACEHOLDER+inputStr.split("\n\n")[-1]
    return inputStr

def switch_to_test_path(path):
    if path.startswith("/story/"):
        return "/test/" + path[len("/story/"):]
    else:
        return path
    
def replace_first(text, str_to_replace, str_replacement):
  """Replaces the first occurrence of string A with string C in text.

  Args:
      text: The string to modify.
      A: The string to be replaced (first occurrence).
      C: The replacement string.

  Returns:
      A new string with the first occurrence of A replaced by C.
  """

  index = text.find(str_to_replace)
  if index != -1:
    return text[:index] + str_replacement + text[index + len(str_to_replace):]
  else:
    return text

def get_bullets_from_html(html, delimeterType="html"):
    import re
    # Define a pattern to match the content within list items (ul or li tags)
    if delimeterType == "html":
        pattern = r"<(ul|li)>(.*?)</(ul|li)>"
        # Extract content from html using findall
        matches = re.findall(pattern, html, flags=re.DOTALL)

        extracted = []
        if matches:
            # Remove tags using re.sub
            extracted = [re.sub(r"<[^>]+>", "", match[1]) for match in matches]
        return extracted
    elif delimeterType == "voice":
        pattern = "<break time=\"1500ms\"/>"
        return html.split(pattern)


def apply_multilingual_voice_extension(filename, language_extension = "en-US"):
    if filename.endswith(".mp3") and not filename.endswith(f".{language_extension}.mp3"):
        return filename[:len(filename)-4] + f".{language_extension}.mp3"

class StoryTranslator:
    @staticmethod
    def exportTranslationScripts(storyFileName):
        print(f"exportTranslationScripts |-> {YELLOW}{storyFileName}{RESET}")
        story = Story.loadFromFile(storyFileName)
        storyScripts = story.exportScripts()
        fullFileName = storyFileName.replace(".json", ".full.scripts.json")
        with open(fullFileName, 'w') as ff:
            json.dump(storyScripts, ff, ensure_ascii=False, indent=4, sort_keys=False)
        storyCompactScripts = []
        compactFileName = storyFileName.replace(".json", ".compact.scripts.json")
        if isinstance(storyScripts, list) and len(storyScripts) > 0:
            for scriptObject in storyScripts:
                for voice in scriptObject["voices"]:
                    if len(voice["transcript"]) > 0:
                        storyCompactScripts.append({"zh-CN": voice["transcript"]} if \
                                                                     isinstance(voice["transcript"], str) else voice["transcript"])    
            with open(compactFileName, 'w') as cf:
                json.dump(storyCompactScripts, cf, ensure_ascii=False, indent=4, sort_keys=False)
        print(f"exportTranslationScripts ->| {YELLOW}{fullFileName}{RESET}, {YELLOW}{compactFileName}{RESET}")

    def __init__(self):
        self._cosUploader = None
        self._synthesizer = None

        QCLOUD_REGION=os.environ.get("QCLOUD_REGION")
        QCLOUD_SECRET_ID=os.environ.get("QCLOUD_SECRET_ID")
        QCLOUD_SECRET_KEY=os.environ.get("QCLOUD_SECRET_KEY")
        QCLOUD_BUCKET=os.environ.get("QCLOUD_BUCKET")
        SERVICE_ROOT="https://resource.dataphi.cn/"

        self._cosUploader = CosUploader(
            service_root=SERVICE_ROOT
            ,cos_region=QCLOUD_REGION
            ,cos_secret_id=QCLOUD_SECRET_ID
            ,cos_secret_key=QCLOUD_SECRET_KEY
            ,cos_bucket=QCLOUD_BUCKET)

        # 创建voice synthesizer对象实例
        AZURE_SPEECH_KEY=os.environ.get("AZURE_SPEECH_KEY")
        AZURE_SPEECH_REGION=os.environ.get("AZURE_SPEECH_REGION")
        self._synthesizer = VoiceSynthesizer(azureSubscription=AZURE_SPEECH_KEY, azureRegion=AZURE_SPEECH_REGION)

    def retrieveTranslation(self, source, translation):
        print(f"retrieveTranslation {YELLOW}{source}{RESET} <- {YELLOW}{translation}{RESET}")
        with open(source, "r") as sf:
            sourceObject = json.load(sf)
        with open(translation, "r") as tf:
            translatedObject = json.load(tf)
        for i, script in enumerate(sourceObject):
            if "en-US" in script and isinstance(script["en-US"], str):
                print(f"Skip translated script {script['zh-CN']}")
                continue
            for translation in translatedObject:
                if script["zh-CN"] == translation["zh-CN"]:
                    sourceObject[i]["en-US"] = concentrak_treatment(translation["en-US"])
            if "en-US" not in script:
                print(f"No match translation for {YELLOW}{script['zh-CN']}{RESET}")
        with open(source, "w") as df:
            json.dump(
                sourceObject, df, ensure_ascii=False, indent=4, sort_keys=False
            )

    def mergeStoryTranslation(self, storyScriptsFileName, translatedScriptsFileName, overwrite=True):
        print(f"mergeStoryTranslation {YELLOW}{storyScriptsFileName}{RESET} <- {YELLOW}{translatedScriptsFileName}{RESET}")
        with open(storyScriptsFileName, "r") as src:
            storyObject = json.load(src)
        with open(translatedScriptsFileName, "r") as tr:
            translatedObject = json.load(tr)
        for i, page in enumerate(storyObject):
            for j, voice in enumerate(page["voices"]):
                if isinstance(voice["transcript"], str):
                    for translation in translatedObject:
                        if translation["zh-CN"] == voice["transcript"] and "en-US" in translation:
                            storyObject[i]["voices"][j]["transcript"] = {"zh-CN": voice["transcript"], "en-US": translation["en-US"]}
                elif isinstance(voice["transcript"], dict) and overwrite:
                    for translation in translatedObject:
                        if translation["zh-CN"] == voice["transcript"]["zh-CN"] and "en-US" in translation:
                            storyObject[i]["voices"][j]["transcript"]["en-US"] = translation["en-US"]
        with open(storyScriptsFileName, "w") as dst:
            json.dump(
                storyObject, dst, ensure_ascii=False, indent=4, sort_keys=False
            )
    
    def buildMultilingualVoice(self, storyScriptsFileName, language='en-US', uploadToCos=True, narrator=None):
        if language == "zh-CN":
            return
    
        if not os.path.exists('./test'):
            os.makedirs('./test')
        outPath = None
        if self._synthesizer != None:
            with open(storyScriptsFileName, "r") as src:
                storyScriptsObject = json.load(src)

            audioUploaded = False
            if isinstance(storyScriptsObject, list):
                for i, page in enumerate(storyScriptsObject):
                    if "voices" in page and isinstance(page["voices"], list):
                        for j, voice in enumerate(page["voices"]):
                            if "sound" in voice and isinstance(voice["sound"], str) and len(voice["sound"]) > 0 \
                                and (narrator == None or (narrator != None and voice.get("narrator", None) == narrator)):
                                try:
                                    destVoiceFileName = voice["sound"]
                                    localVoiceFileName = apply_multilingual_voice_extension(destVoiceFileName, language_extension=language)
                                    localVoiceFileName = switch_to_test_path(localVoiceFileName)
                                    localPath, localFileName = os.path.split(localVoiceFileName)
                                    if localPath.startswith("/"):
                                        localPath = "." + localPath
                                    if not os.path.exists(localPath):
                                        os.makedirs(localPath)
                                    if outPath != localPath:
                                        outPath = localPath
                                        print(f"\n========Multilingual voice files exported to {outPath}========\n")
                                    
                                    finalScript = voice["transcript"][language+".alt"] if language+".alt" in voice["transcript"] else voice["transcript"][language]
                                    self._synthesizer.synthesizeFile(
                                        voice["narrator"], remove_emojis(finalScript), language, localPath, localFileName
                                    )
                                    #time.sleep(5)
                                    localOutputFileName = os.path.join(localPath, localFileName)

                                    remotePath, _ = os.path.split(destVoiceFileName)
                                    if remotePath.startswith("/"):
                                        remotePath = remotePath[1:]
                                    if self._cosUploader != None and uploadToCos:
                                        _ = self._cosUploader.local2cos(localOutputFileName, "", remotePath)
                                        audioUploaded = True
                                except Exception as e:
                                    print(f"failed to generate multilingual voice for {RED}{destVoiceFileName}{RESET}")
                                    continue
                                if "languages" in voice and isinstance(voice["languages"], list) \
                                    and language not in voice["languages"]:
                                    storyScriptsObject[i]["voices"][j]["languages"].append(language)
                                else:
                                    storyScriptsObject[i]["voices"][j]["languages"] = [language]
                if audioUploaded:
                    with open(storyScriptsFileName, "w") as dst:
                        json.dump(
                            storyScriptsObject, dst, ensure_ascii=False, indent=4, sort_keys=False
                        )
    
    def _lookupTranslation(self, multilingualObject, key):
        if not has_chinese_char(key):
            return key
        
        for page in multilingualObject:
            if "voices" in page and isinstance(page["voices"], list) and len(page["voices"]) > 0:
                for mVoice in page["voices"]:
                    if "transcript" in mVoice and isinstance(mVoice["transcript"], dict) \
                        and "zh-CN" in mVoice["transcript"] and "en-US" in mVoice["transcript"]:
                        if key == mVoice["transcript"]["zh-CN"]:
                            return {"zh-CN": mVoice["transcript"]["zh-CN"], "en-US": mVoice["transcript"]["en-US"]}
        print(f"_lookupTranslation: No translation for [{RED}{key}{RESET}]")
        return key

    def updateStoryWithMultilingualResource(self, storyFileName, multilingualScriptsFileName):
        print(f"updateStoryWithMultilingualResource {YELLOW}{storyFileName}{RESET} <- {YELLOW}{multilingualScriptsFileName}{RESET}")
        with open(storyFileName, "r") as src:
            storyObject = json.load(src)
        with open(multilingualScriptsFileName, "r") as tr:
            multilingualObject = json.load(tr)

        if "voices" in storyObject and isinstance(storyObject["voices"], list) \
            and "events" in storyObject and isinstance(storyObject["events"], list):
            for i, storyVoice in enumerate(storyObject["voices"]):
                for page in multilingualObject:
                    if "voices" in page and isinstance(page["voices"], list) and len(page["voices"]) > 0:
                        for mVoice in page["voices"]:
                            if not isinstance(mVoice["transcript"], dict):
                                continue
                            if mVoice.get("sound", None) != None and storyVoice["sound"] == mVoice["sound"] and "languages" in mVoice:
                                storyObject["voices"][i]["languages"] = mVoice["languages"] \
                                    if ("languages" not in storyVoice or len(storyVoice["languages"]) == 0) \
                                    else list(set(storyVoice["languages"]) | set(mVoice["languages"]))
            for j, storyEvent in enumerate(storyObject["events"]):
                if "board" in storyEvent and isinstance(storyEvent["board"], dict):
                    if "content" in storyEvent["board"] and isinstance(storyEvent["board"]["content"], dict):
                        content = storyEvent["board"]["content"]
                        for key in ("caption", "question"):
                            if key in content:
                                result = self._lookupTranslation(multilingualObject, \
                                            content[key] if isinstance(content[key], str) else content[key]["zh-CN"])
                                if result != None:
                                    storyObject["events"][j]["board"]["content"][key] = result
                        if "html" in content:
                            if content["html"] != None:
                                original_str = content["html"] if isinstance(content["html"], str) else content["html"]["zh-CN"]
                                destination_str = original_str
                                bullets = get_bullets_from_html(destination_str, delimeterType="html")
                                bulletsVoiceScript = VOICE_BREAK_TAG.join(bullets)
                                result = self._lookupTranslation(multilingualObject, bulletsVoiceScript)
                                if result != None:
                                    sourceBullets = result["zh-CN"].split(VOICE_BREAK_TAG)
                                    destinationBullets = result["en-US"].split(VOICE_BREAK_TAG)
                                    if (len(sourceBullets) == len(destinationBullets)):
                                        for k in range(len(sourceBullets)):
                                            destination_str = replace_first(destination_str, sourceBullets[k], destinationBullets[k])
                                        storyObject["events"][j]["board"]["content"]["html"] = {"zh-CN": original_str, "en-US": destination_str}
                                    else:
                                        print(f"Non-equivelant bullets, ignore: {RED}{original_str}{RESET}")
                        if "options" in content:
                            if content["options"] != None:
                                mOptions = []
                                mAnswer = []
                                if isinstance(content["options"], list):
                                    for option in content["options"]:
                                        result = self._lookupTranslation(multilingualObject, option) if len(option) > 0 else option
                                        mOptions.append(result if isinstance(result, str) else (result["en-US"] if result.get("en-US", None) != None else option))
                                    if mOptions != content["options"]:
                                        storyObject["events"][j]["board"]["content"]["options"] = {"zh-CN": content["options"], "en-US": mOptions}
                                elif isinstance(content["options"], dict) and isinstance(content["options"].get("zh-CN", None), list):
                                    for option in content["options"]["zh-CN"]:
                                        result = self._lookupTranslation(multilingualObject, option) if len(option) > 0 else option
                                        mOptions.append(result if isinstance(result, str) else (result["en-US"] if result.get("en-US", None) != None else option))
                                    storyObject["events"][j]["board"]["content"]["options"]["en-US"] = mOptions
                                if isinstance(content.get("answer", None), list):
                                    for answer in content["answer"]:
                                        for k, opt in enumerate(content["options"]["zh-CN"] if isinstance(content["options"], dict) else content["options"]):
                                            if answer == opt:
                                                mAnswer.append((content["options"]["en-US"] if isinstance(content["options"], dict) else content["options"])[k])
                                    if mAnswer != content["answer"]:
                                        storyObject["events"][j]["board"]["content"]["answer"] = {"zh-CN": content["answer"], "en-US": mAnswer}
                                elif isinstance(content.get("answer", None), dict) and isinstance(content["answer"].get("zh-CN", None), list):
                                    for answer in content["answer"]["zh-CN"]:
                                        for k, opt in enumerate(content["options"]["zh-CN"]):
                                            if answer == opt:
                                                mAnswer.append(content["options"]["en-US"][k])
                                    storyObject["events"][j]["board"]["content"]["answer"]["en-US"] = mAnswer


                    if "contentList" in storyEvent["board"] and isinstance(storyEvent["board"]["contentList"], list):
                        for k, contentEntry in enumerate(storyEvent["board"]["contentList"]):
                            if "caption" in contentEntry and (len(contentEntry["caption"])>0 if isinstance(contentEntry["caption"], str) \
                                                              else len(contentEntry["caption"]["zh-CN"]) > 0):
                                result = self._lookupTranslation(multilingualObject, \
                                            content["caption"] if isinstance(content["caption"], str) else content["caption"]["zh-CN"])
                                if result != None:
                                    storyObject["events"][j]["board"]["contentList"][k]["caption"] = result
                if "interactions" in storyEvent and isinstance(storyEvent["interactions"], list):
                    for k, interaction in enumerate(storyEvent["interactions"]):
                        if "content" in interaction and isinstance(interaction["content"], dict) and "text" in interaction["content"]:
                            text = interaction["content"]["text"]
                            key = text["zh-CN"] if isinstance(text, dict) else text
                            result = self._lookupTranslation(multilingualObject, key) if len(key) > 0 else key
                            if result != None:
                                storyObject["events"][j]["interactions"][k]["content"]["text"] = result

            with open(storyFileName, "w") as dst:
                json.dump(
                            storyObject, dst, ensure_ascii=False, indent=4, sort_keys=False
                        )
            print(f"Update story with multilingual resource on {storyFileName} from {multilingualScriptsFileName}")


if __name__ == "__main__":
    # action_param: "export" ...
    action_param = sys.argv[1]
    # source_param: <story json title>.json
    source_param = sys.argv[2]
    # additional_param: <story json title>.translated.json
    additional_param = sys.argv[3] if len(sys.argv) > 3 else None

    if action_param in ("export"):
        assert (source_param != None)
        StoryTranslator.exportTranslationScripts(source_param)
    else:
        assert (source_param != None and source_param.endswith(".json"))
        translator = StoryTranslator()
        
        storyFile = source_param
        storyCompactScripts = storyFile.replace(".json", ".compact.scripts.json")
        storyFullScripts = storyFile.replace(".json", ".full.scripts.json")
        storyTranslatedScripts = storyFile.replace(".json", ".translated.json") if additional_param == None else additional_param

        if action_param in ("step1", "retrieve", "fullprocess"):        
            translator.retrieveTranslation(storyCompactScripts, storyTranslatedScripts)
        
        if action_param in ("merge", "step2", "fullprocess"):
            translator.mergeStoryTranslation(storyFullScripts, storyCompactScripts, overwrite=True)
        
        if action_param in ("synthesize", "step2", "fullprocess"):
            narrator = None
            if action_param == "synthesize" and additional_param.lower() in ("girl", "boy", "eily", "eilly", "f", "m", ""):
                narrator = additional_param
                uploadToCos = sys.argv[4].lower() in ("false", "f") if len(sys.argv) > 4 else True
            translator.buildMultilingualVoice(storyFullScripts, language='en-US', uploadToCos=True, narrator=narrator)
        
        if action_param in ("update", "step2", "fullprocess"):
            translator.updateStoryWithMultilingualResource(storyFile, storyFullScripts)
