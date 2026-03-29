---
description: Do not use browser_subagent for testing unless the user explicitly asks
---

## Rule: No Browser Testing

- **절대** `browser_subagent` 도구를 사용하여 프론트엔드를 테스트하지 마세요.
- 사용자가 직접 "브라우저 테스트해줘", "확인해줘", "verify in browser" 등 **명시적으로 요청**하기 전까지 브라우저 테스트를 시도하지 않습니다.
- 에러가 발생해도 **코드를 직접 읽고 분석**하거나, **서버 로그를 확인**하는 방식으로 디버깅합니다.
- 브라우저 스크린샷이 필요하면 사용자에게 요청합니다.
