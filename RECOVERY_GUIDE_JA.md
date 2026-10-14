# Instagram自動投稿 復旧手順
更新日: 2026-10-15 JST。最後の実診断は2026-10-14。過去の成功記録は現在の認証正常を保証しない。

## 現状と役割
- 運用: Canvaで制作、GitHub Actionsで公開、Google Driveは補助素材・完成物保存。Metricool不使用。
- 時刻スキップのコード不備は修正済み。Instagram /me はHTTP400/code200/OAuthException/API access blocked、Canva更新はHTTP400/invalid_grantを確認した。アプリ制限の詳細、トークンが無効になった理由の内訳は未確定。
- 本人操作: Meta/Canvaのログイン・同意・秘密情報登録。こちら: 設定確認、コード修正、テスト、公開確認。シークレットの値はGitHub連携から読み出せない。

## 0. 復旧中の投稿を一時停止
GitHubリポジトリ https://github.com/o9o84441100-droid/panipani-instagram-auto のActionsで「Panipani genuine Canva Reels automatic publishing」を開き、メニューのDisable workflowを使う。これは復旧中の一時停止。元の投稿履歴は削除しない。検証用ワークフローは停止しない。現在実行中の公開ジョブがあれば、まずInstagram公開状態とログを照合してから扱う。

## 1. Instagram
1. https://developers.facebook.com/apps/ を開き、既存「Panipani Auto Publisher」を選ぶ。別アプリを新規作成しない。
2. ダッシュボードの制限・無効化・必要な対応・権限・ログイン接続の表示を確認。表示される対応を先に完了する。「公開モードにすれば必ず直る」「新トークンで必ず解除される」と判断しない。制限があれば、必要な異議申立て/審査/確認を行う。
3. Instagram > API setup with Instagram business login（InstagramビジネスログインによるAPI設定）を確認。UI名は表示言語・アプリ構成で異なる。
4. 対象が@reiv2220で、プロアカウントの接続と本人の役割・招待承認を確認。基本参照と投稿の権限 instagram_business_basic / instagram_business_content_publish を確認。他のログイン方式の権限・トークンと混同しない。
5. 制限が解消し必要権限が揃ったら、対象アカウント横のGenerate token（トークン生成）から許可し、新しいInstagram用トークンを取得。有効期限も確認。Facebookページ用トークンを代用しない。
6. GitHub > Settings > Secrets and variables > Actions > Repository secretsでINSTAGRAM_ACCESS_TOKENを編集・更新。値だけを貼り、Bearerや引用符・余計な改行を付けない。
7. Actionsの「Instagram API connection check」を開く。Run workflow、mainを選び実行。これは投稿しない。
8. 緑色だけでなくログでConnected account: reiv2220、Publishing quota usage、CHECK ONLYを確認。API access blocked継続ならここで止め、エラーとMetaの状態表示を調べる。/me成功だけでも、公開APIまで正常と確定しない。

## 2. Canvaを新規認証
CanvaのChatGPT連携と、GitHub用Canva OAuthは別。今回必要なのは後者。
1. 既存CanvaアプリをDeveloper Portalで開く。Client ID、登録済みRedirect URL、選択済みScopesを確認。既存Client Secretを手元で用意し、他人に送らない。Client SecretやCANVA_TOKEN_KEYをむやみに再発行しない。
2. PCにPython 3を用意する。tools/canva_reauthorize_local.pyをローカルPCへダウンロードする。このスクリプト自体に秘密情報はない。
3. Windowsは py canva_reauthorize_local.py、Mac/Linuxは python3 canva_reauthorize_local.py を実行。
4. Existing Canva Client IDに既存ID、Client Secretに既存秘密鍵（入力非表示）、Exact registered Redirect URLに設定と完全一致するURL、Existing enabled scopesに既存の必要スコープを半角スペース区切りで入力。
5. スコープやRedirect URLが不明なら推測で入力しない。Developer PortalのOutside Canva > Redirect URLs/認証設定を確認する。
6. 開いたCanva公式画面で、正しいアカウント・チームを選び同意する。
7. 同意後の転送先URL全文を、チャットではなくPCのプログラムの入力欄へ貼る。転送先が既存のローカル受け取り先で、ローカルサーバー未起動のため開けない場合でも、ブラウザにcodeとstateを含む転送URLが残れば入力できる。他人が管理する転送先は使わない。
8. スクリプトがstateと転送先を検証し、認可コードをトークンに交換する。新しいrefresh_tokenだけをPCホームのcanva-new-refresh-token.txtへ保存する。秘密の値を画面やログへ表示しない。
9. 既に同名ファイルがある場合は上書きしない仕様。以前の不要ファイルか確認して安全に削除してから、新しい認証フローを最初から実行する。
10. これは構文確認済みの補助スクリプトで、本人の環境での実認証成功はまだ未確認。エラー時は秘密の値を送らずエラー種別だけ共有する。

## 3. Canva認証をGitHubへ登録
1. GitHub Settings > Secrets and variables > Actions > Repository secretsを開く。
2. CANVA_REFRESH_TOKENだけを新しいcanva-new-refresh-token.txtの内容へ更新する。CANVA_CLIENT_ID/CLIENT_SECRETは同じアプリなら維持。CANVA_TOKEN_KEYも維持する。
3. Actions > Restore Canva OAuth after owner reauthorization > Run workflow > main。これは新しいトークン登録後に一度だけ実行する。
4. 成功ログ「Canva reauthorization verified and rotating credential saved. No Instagram publication.」を確認。
5. 成功後に同じ新規認証用ワークフローを繰り返さない。一度使ったCANVA_REFRESH_TOKENシークレットをまた再交換しない。通常処理はstate/canva/refresh_token.encの最新値へ引き継ぐ。
6. 確認後、PCの平文トークンファイルを削除し、コピーしたクリップボードも消す。チャット・Drive・Git・Issueへアップロードしない。
7. invalid_grantが続く場合は、更新した値、アプリ・チーム・Client ID、コード交換と更新トークンの取り違えを確認。連打しない。

## 4. 公開しないCanva制作テスト
1. Actions > Panipani - live Canva export TEST (never posts to Instagram) > Run workflow > main > template=all。
2. 全処理成功後、Artifactsのpanipani-real-canva-export-testをダウンロード・展開。
3. 3本を実際に再生し、先頭・途中・末尾の文字重なり、切れ、背景、音、内容を確認。映像1080x1920/H.264、音AACを確認。
4. このallは既存の3テンプレートの確認。実写テンプレートが追加されたことを意味しない。

## 5. 実写テンプレートの自動化
- 優先はCanvaの利用可能な実写写真・動画と実際のリールテンプレート。Driveに素材がなくても制作可。
- 元「黒と白 シンプル 習慣 暮らし リール動画」はDAHX5ScAlSk。作業コピーDAHX5Y7yKgQは確認時点でdataset空。
- 作業コピーを保存・確認し、投稿形式に合わせた自動差替え項目を設定する必要がある。
- 現行制作コードはHOOK/SITUATION/PROMPT/CAUTION/CTAの5項目を要求する。1枚表紙に無理に5項目を詰めず、必要なら本文ページを備えるテンプレートか、対応する制作コードを用意する。
- dataset確認、実動画書き出し、表示確認、権利確認後にCANVA_TEMPLATE_IDSへ追加する。IDを先に足すだけではエラーになる。
- 実写に見えるAI画像と実写写真は区別し、素材をレイ本人の来店・暮らしと偽らない。
- 昨日の添付MP4は512x910。1080x1920へ拡大しても細部の画質が増えるわけではない。可能ならCanva元デザインから高解像度で出力する。

## 6. 1件だけ公開テストして再開
1. Instagram接続、Canva認証、実写テンプレートQAのすべてを確認後、日次投稿workflowをEnable workflowで再開する。
2. Run workflowは、当日まだ公開していない適切な時間帯の枠を一つ選ぶ。朝枠の残りを夜にまとめて投稿しない。必要ならこちらで枠を確認して実行する。
3. 公開中は連打しない。state/postsの対象記録、Instagram media ID、permalink、実公開URLを照合する。
4. GitHubの緑は公開成功の証拠ではない。publish=skippedなら未投稿。published_unverifiedはURL未確認。
5. 失敗した場合はAPIが受理済みかを確認してから再実行する。媒体IDが返った後の台帳保存失敗は二重投稿の危険がある。
6. 最初の1件、翌日の5枠、次の数日を分けて確認。起動時刻はGitHubの遅延によりずれる場合があり、分単位の正確な公開を保証しない。

## 維持する予定
朝分析07:30。投稿目標08:05/10:05/12:05/18:05/21:05。GitHub補助確認は毎時17分、最大1件の当日直近枠を確認し早出し/古い枠のまとめ投稿を防ぐ。Drive保存は毎時15分。成果報告23:50。

## 送ってよい確認情報
エラー文、失敗step名、GitHub run URL、アプリの制限表示（秘密情報を隠す）、作業完了の連絡。
送らないもの: アクセストークン、refresh_token、Client Secret、CANVA_TOKEN_KEY、認可コードを含む転送URL。

## 参照
- Meta: https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/get-started
- Canva OAuth: https://www.canva.dev/docs/apps/rest-apis/authentication/
- Canva token endpoint: https://www.canva.dev/docs/apps/rest-apis/reference/authentication/generate-access-token/
- GitHub Secrets: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
