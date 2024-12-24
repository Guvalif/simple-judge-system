機械学習評価システムの構築
===============================================================================

## 要求

- SIGNATE の要領で、CSV をアップロードすると正解率を返すような、Web API を構築したい
- 保守性や拡張性の観点から、Python で実装を行いたい
- AWS や Google Cloud などのプラットフォームによらずに、動作を担保するために Docker Image としてパッケージングを行いたい


## 機能要件

- `/judge` というエンドポイントに対して、`application/x-www-form-urlencoded` 形式で CSV を POST できる
- CSV は下記の形式のみを受け付けることができる：


|index    |class   |
|:--------|:-------|
|`integer`|`string`|

- もし不正な形式の CSV が POST された場合、[400 Bad Request](https://developer.mozilla.org/ja/docs/Web/HTTP/Status/400) でレスポンスを返す
- 正常な形式の CSV が POST された場合、事前に用意された `index` と `class` の組にしたがって、正解率をレスポンスとして返す
- `/judge` 以外のエンドポイントに対してアクセスがあった場合、[404 Not Found](https://developer.mozilla.org/ja/docs/Web/HTTP/Status/404) でレスポンスを返す


## 非機能要件

- 管理者に相当するアクターは、事前に用意された `index` と `class` の組を、簡単に取り替えることができる
- ユーザーは、Web UI を通じて、簡単に動作確認を行うことができる


## Development Commands

- `docker build . -t guvalif/gdg`
- `docker run --rm -p 8080:8080 guvalif/gdg`
