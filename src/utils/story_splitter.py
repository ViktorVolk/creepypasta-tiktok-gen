class StorySplitter:
    def split(self, story: str) -> tuple[str, str, str]:
        if not isinstance(story, str) or not story.strip():
            raise ValueError("Рассказ должен быть непустой строкой")

        paragraphs = [p.strip() for p in story.split('\n') if p.strip()]
        
        if len(paragraphs) >= 3:
            third = len(paragraphs) // 3
            
            mid1 = third
            for i in range(mid1, len(paragraphs)):
                if paragraphs[i].strip().endswith(('.', '!', '?')):
                    mid1 = i + 1
                    break
            
            mid2 = 2 * third
            for i in range(mid2, len(paragraphs)):
                if paragraphs[i].strip().endswith(('.', '!', '?')):
                    mid2 = i + 1
                    break
            
            part1 = '\n\n'.join(paragraphs[:mid1])
            part2 = '\n\n'.join(paragraphs[mid1:mid2])
            part3 = '\n\n'.join(paragraphs[mid2:])
        else:
            sentences = story.split('. ')
            third = len(sentences) // 3
            
            mid1 = third
            for i in range(mid1, len(sentences)):
                if sentences[i].strip().endswith(('.', '!', '?')):
                    mid1 = i + 1
                    break
            
            mid2 = 2 * third
            for i in range(mid2, len(sentences)):
                if sentences[i].strip().endswith(('.', '!', '?')):
                    mid2 = i + 1
                    break
            
            part1 = '. '.join(sentences[:mid1])
            part2 = '. '.join(sentences[mid1:mid2])
            part3 = '. '.join(sentences[mid2:])
        
        part1_words = len(part1.split())
        part2_words = len(part2.split())
        part3_words = len(part3.split())
        total_words = part1_words + part2_words + part3_words
        
        if total_words > 0:
            max_words = max(part1_words, part2_words, part3_words)
            min_words = min(part1_words, part2_words, part3_words)
            ratio = (max_words - min_words) / max_words if max_words > 0 else 0
            
            if ratio > 0.2:
                words = story.split()
                third_word = len(words) // 3
                
                mid1_word = third_word
                for i in range(mid1_word, len(words)):
                    if words[i].endswith(('.', '!', '?')):
                        mid1_word = i + 1
                        break
                
                mid2_word = 2 * third_word
                for i in range(mid2_word, len(words)):
                    if words[i].endswith(('.', '!', '?')):
                        mid2_word = i + 1
                        break
                
                part1 = ' '.join(words[:mid1_word])
                part2 = ' '.join(words[mid1_word:mid2_word])
                part3 = ' '.join(words[mid2_word:])
        
        return part1, part2, part3
