# hakushu-watch

サントリー白州・山崎・響の抽選販売告知をweb上から検出してLINE個人アカウントへPush通知する個人用モニター。応募は人間が手動で実施します。

## 監視対象

- nyuka-now.com（白州・山崎・響まとめ、在庫・再販まとめ）
- norifune.com（白州購入情報）
- suntory.co.jp（白州・山崎・響の商品ページ、白州蒸溜所News）
- search.rakuten.co.jp（白州・山崎・響の楽天ふるさと納税検索結果）
- takashimaya.co.jp（高崎高島屋トップページ、オンラインストア ウイスキーラウンジ）

## やらないこと

- Amazon等の自動購入（規約違反）
- 抽選への自動応募（規約違反店舗多数）
- X(Twitter)監視（公式API有料化＋nitter停滞のため依存断ち）

## セットアップ

### 1. GitHubリポジトリ作成

`hakushu-watch` という名前で **public** リポジトリを作成し、本ディレクトリをpush。public にするのは GitHub Actions を無料の枠で使うため。

### 2. LINE Messaging API チャネル作成

1. [LINE Developers Console](https://developers.line.biz/) にログイン
2. **Provider** → 新規作成（個人名でOK）
3. **Messaging API channel** を新規作成
4. 「Messaging API設定」タブで **チャネルアクセストークン（長期）** を発行
   - **重要**: 短期トークンは1ヶ月で切れるため必ず長期を選ぶ
5. 同タブのQRコードを iPhone のLINEで読み取り、自分の公式アカウントを「友だち追加」

### 3. LINE User ID 取得

LINE Developers画面に表示される「Your user ID」は LIFF用で別物のため使えない。Webhookイベント経由で取得する：

```bash
# ターミナル1: プロジェクト直下で受信スクリプトを起動（標準ライブラリのみで動く、:8000で待機）
python -m tools.dump_user_id

# ターミナル2: 一時的な公開URLを発行する。インストール不要で macOS 標準の ssh だけで動く。
ssh -R 80:localhost:8000 nokey@localhost.run
# → "Connect to ... https://xxxxxxxx.lhr.life" のような URL が表示される

# （ngrok派の人は: ngrok http 8000 でもOK）
```

Developers Console の「Webhook URL」に上記URL + `/webhook` を設定して **Webhookの利用** をON、「応答メッセージ」はOFF推奨。
その後、自分のLINEから公式アカウントに何でもメッセージを1通送ると、ターミナル1のコンソールに `>>> LINE_USER_ID = U....` が表示されるのでメモ。
取得後はトンネルとスクリプトをCtrl-Cで終了してOK。

### 4. GitHub Secrets 設定

リポジトリの **Settings → Secrets and variables → Actions** で以下を登録：

| Name | Value |
|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | 手順2で発行したトークン |
| `LINE_USER_ID` | 手順3で取得したUser ID（`U` で始まる文字列） |

### 5. 動作確認

```bash
# 依存解決
pip install -e .

# 各ソース取得＋ハッシュ計算（LINE通知はしない）
python -m src.main --dry-run

# LINE通知の単体テスト
LINE_CHANNEL_ACCESS_TOKEN=xxx LINE_USER_ID=Uxxx python -m src.notifier.line --test

# テスト
pytest
```

GitHub Actions側は **Actions タブ → poll → Run workflow** で初回手動実行。
state branch (`state`) に `state.json` が作成されることを確認したら、cronが15分毎に自動実行されます。

## 実行間隔

GitHub Actions cronは仕様上 5〜15分の遅延（混雑時は最大1時間）があるため、実効は15分前後。応募期間が48時間以上ある抽選には十分間に合います。

## 状態管理

`state` orphan branchに `state.json` をforce pushする。各ソースの前回ハッシュと抜粋を保持。

## ローカル動作

```bash
# state はデフォルトで state/state.json
python -m src.main --dry-run
```

`state/state.json` は `.gitignore` に入れているのでローカル開発で混入しない。

## メンテナンス

- **HTML構造変更でセレクタが効かなくなった場合**: fallbackが発動し「セレクタ要更新」フラグ付きで通知が来る。`src/sources/*.py` のセレクタを更新
- **403対策はデフォルトで curl_cffi (Chrome TLS fingerprint) を使用済み**。サントリー (Akamai WAF) で必要だったため。それでも弾かれる新サイトが出たら `impersonate="chrome120"` などバージョン指定を試す
- **誤検知が多い場合**: `src/core/hash.py` の `NOISE_PATTERNS` に正規表現を追加

## 法的・倫理的境界

- 利用目的は自家消費・贈答・長期保管（投資的所有含む）の範囲内。**継続的な転売は酒類小売業免許が必要で、無免許は酒税法違反**
- スクレイピング先のrobots.txtを尊重、巡回間隔は15分（各サイト1日96リクエスト＝無害範囲）
