# API Server Practice

## Elevator
2019 카카오 코딩테스트 때 출시된 엘리베이터 문제입니다.
[[블로그]](https://tech.kakao.com/2018/10/23/kakao-blind-recruitment-round-2/)
[[Github]](https://github.com/kakao-recruit/2019-blind-2nd-elevator)

해당 모듈에는 엘리베이터 문제를 풀기위한 에뮬레이션 서버가 들어있습니다. (python 서버 구축 연습겸 작성한 것입니다.)

### Run Server
서버는 `docker`를 사용하여 실행되기 때문에 도커가 설치되어 있어야 합니다. `elevator` 서버는 발행된 토큰별 저장소를 보장하기 위해 **redis**를 사용하였고, **pickle**을 이용하여 저장하였습니다.

실행 명령어는 다음과 같습니다.
```console
$ docker compose up
or in background,
$ docker compose up -d
```

`docker compose`의 자동 서브넷 구성설정을 이용하여 **redis** 서버와 통신하게끔 되어있습니다.

데이터 구성은 원본 깃허브 코드에서 그대로 가져온 것입니다. 데이터 구성도 같지만 만약 새로운 데이터를 추출하기 위해서는 다음 명령어를 **컨테이너 내부**에서 입력하시면 됩니다.

```console
# flask elevator generate
```

엘리베이터와 관련된 데이터를 모두 지우고 싶으면 아래 명령어를 입력하시면 됩니다.

```console
# flask elevator clean-redis
```

도커를 실행시키면 기본적으로 `8080`포트로 시작됩니다.
API 서버 URL은 기본적으로 `/elevator` 라는 prefix가 붙습니다. 따라서 API 요청시 base url를 http://localhost:8080/elevator 로 API 요청을 하면 되고, 카카오 깃헙에서의 viewer를 일부 케이스에서는 지원합니다. (http://localhost:8080/elevator/viewer)

### Solver
[Here is a code](elevator-solver/solver.py)

### Result

위 구현된 서버가 아닌 카카오에서 제공된 시뮬레이션 서버를 이용하여 도출한 결과입니다.

|            | Timestamp | AveWait  | AveTravel | AveTotal |
|------------|-----------|----------|-----------|----------|
| 어피치 멘션 | 13        | 3.00000  | 5.66667   | 8.66667  |
| 제이지 빌딩 | 569       | 24.33500 | 28.05000  | 52.38500 |
| 라이언 타워 | 1867      | 10.55000 | 16.96000  | 27.51000 |
