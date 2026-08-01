# V2 Backlog

Simple tracker for gaps between the current implementation and the diploma V2 scope.

## Features To Add

- Implement VK channel as a real app entry point instead of placeholder `/app` behavior.
- Implement external translation/dictionary architecture as described in V2.
- Add Redis-backed rate limiter for bot and external service requests.
- Add unified learner progress tracking across quizzes, repetitions, and games.
- Store game results for Hangman and Speed Typing.
- Add production deployment stack: Nginx, Django, PostgreSQL, Redis, translation service, dictionary service.
- Configure PostgreSQL for deployed/runtime environments.

## Bugs To Fix

- Fix role checks: call `is_student()` and `is_teacher()` methods consistently.
- Scope deck/card reads, updates, deletes, and API output to the current owner.
- Fix cards API query path for the current `Deck.student -> User` relationship.
- Fix SM-2 scheduling for new cards and avoid invalid recursion.
- Save card review history when a flashcard rating is submitted.
- Remove hard-coded ngrok host and fallback username from game JavaScript.
- Make Telegram WebApp user/card loading use the authenticated user reliably.
- Replace VK `/app` Google link with the actual application URL.
- Fix flashcards session completion/result handling.

## Refactoring

- Separate bot platform clients from command handling for Telegram and VK.
- Introduce service interfaces for translation and dictionary providers.
- Move rate-limiter code into a dedicated module.
- Centralize ownership checks for student-owned resources.
- Align naming and data model details with the diploma V2 schema where practical.
