
 # 뉴스 요약 AI speaker & 웹 사이트 NEWSSUM
 
 ### 기간  
 2022.5.2.~2022.6.7.  
 
 ### 내용   
 STT를 사용해 키워드, 뉴스 주제를 입력 후 해당 뉴스 요약문을 google TTS를 사용해 스피커로 출력 & FAST API를 사용 웹 페이지 구현  
 
 ### 상세 과정
 
연예,스포츠,정치등 6개 분야 네이버 뉴스 6개의 기사 크롤링(beautifulsoup4) ‘xxx 키워드 검색‘ 입력시 xxx를 검색 후 관련 뉴스 크롤링(Selenium) -> 크롤링한 뉴스 기사 전처리 후 Kobart 모델링 후 요약기사 생성 -> 기사 본문, 언론사, 요약 뉴스등 7개의 정보 RDS에 적재 -> FastAPI로 뉴스 주제 음성 입력시 해당 주제 뉴스 기사 요약문 3개 or 검색하고 싶은 키워드 음성 입력시 해당 기사 요약문 1개를 response 하는 api 생성 -> 라즈베리파이 4에 해당 api 호출 함수 생성 -> 요약 뉴스 TTS 출력  
 ### 사용 기술 stack
 
 ![image](./stack.png)


### 인원 및 역할
- 총원 4명 
- 역할 : 영화 정보 크롤링, 웹 페이지 구현

### 상세 역할
**< part (1) : 영화 정보 크롤링 >**    
- beautifulsoup4 활용 영화 제목, 감독, 개봉정보, 줄거리 등 10개 정보 크롤링(2011~2019)
- 크롤링 한 데이터 csv 형태로 Django 자체 db에 저장  

**< part (2) : 웹 페이지 구현 >**  
- django 활용 키워드 검색 추천 웹 페이지 구현  

## 프로젝트 결과

[![mv](https://img.youtube.com/vi/AfWimVqh24s/hqdefault.jpg)](https://www.youtube.com/watch?v=AfWimVqh24s)


### 개선 사항
- 검색시 속도 문제 해결 필요
- 웹 서버 배포를 통해 홈페이지 구현
- 키워드 기반 추천 방식 외에 다른 추천 시스템 방식 도입 
