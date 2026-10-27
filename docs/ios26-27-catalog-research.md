# iOS 26・27 カタログの調査結果

## 対象と根拠の強さ

ShortcutForgeは、アクションの存在・引数・列挙値・OS版差分を別々の根拠として記録します。名称だけが公開された項目は、内部IDやシリアライズ形式まで確認できた扱いにしません。

| OS版 | 識別子 | 引数 | 変更履歴 | 実機動作 |
|---|---|---|---|---|
| iOS 26 | 完全な公開スナップショットなし | 完全な公開スナップショットなし | Apple公式リリースノートとコミュニティ比較を個別収録 | このWindows環境では未検証 |
| iOS 27 | 1,206件。iOS 27 Simulator ToolKit v78（2026-06-13） | iOS 27として記録された引数キー・型・表示順・フラグ・列挙値 | 26→27の公開比較を個別収録 | このWindows環境では未検証 |

## iOS 27の機械可読データ

`action_catalog.json` のiOS 27観測済み1,206 IDは、固定したToolKit v78スナップショットのID一覧と完全一致します。1,146件に表示名の情報があり、1,072件にiOS 27引数データがあります。引数キーは合計3,432件です。列挙型は815型・859パラメータ参照を照合し、4,676個の一意な選択肢（パラメータへの重複参照を含めると4,906件）を該当パラメータに埋め込みました。選択肢は`id`と表示用`title`を保ちます。

データは`src/shortcutforge/data/source-snapshots/toolkit-v78/`に固定し、`tools/import_ios26_27_catalog.py`で再取り込みできます。取得元は[viticci/shortcuts-playground-plugin](https://github.com/viticci/shortcuts-playground-plugin/tree/2de03bffe4ce8802e06d184931d9e4ec366a2ef2)。同リポジトリのMITライセンス表記は[`viticci-LICENSE`](../src/shortcutforge/data/viticci-LICENSE)を参照してください。元スナップショットは配布wheelに含めません。

ToolKitのiOS 27データはSimulator上の観測です。インストールされていない標準アプリ、端末機能、コントロールフローなどが欠ける可能性があります。表示名や引数メタデータは、アクションが全端末・全地域で利用可能であることや、ShortcutForgeが正しい実行用plistを生成できることを保証しません。

## iOS 26の機械可読変更履歴

`version_changes.json`はiOS 26.0のApple公式ノートに掲載された追加アクションを個別行にし、iOS 26.1と26.4のコミュニティ報告も個別の追加・改称・パラメータ変更として記録しています。iOS 27はApple公式の27.0と27.2のアクション・自動化・編集機能の変更も加えました。iOS 26.4の「マルチタスクモード」はiPadOS/macOS向けとして、iOS対応が確認されていないことを明記します。

Apple公式のiOS 26ノートは[こちら](https://support.apple.com/en-gb/125148)。26.1および26.4の比較は[Automators 26.1](https://talk.automators.fm/t/ios-18-26-1-new-and-updated-actions/19029)、[Automators 26.2–26.4](https://talk.automators.fm/t/os-26-2-26-4-new-and-updated-actions/19117)を参照します。Appleの[About iOS 26 Updates](https://support.apple.com/en-ie/123075)で26.5〜26.7.1も確認しましたが、この範囲では新しいショートカットアクション名の告知は見つかりませんでした。これは非公開の変更がないことを証明するものではありません。これらの記録は表示名称や説明の出典であり、完全な内部ID一覧ではありません。

### iOS 26で埋まっていないもの

Appleは全アクションの内部ID、plist引数スキーマ、enum値を網羅した公式一覧を公開していません。公開されているiOS 27 SimulatorデータからiOS 26の互換性を逆算することもしません。そのため、iOS 26の通常アクション全件の正確な内部ID・引数スキーマは、信頼できる公開根拠が見つかるまで`unknown`のままです。これは未調査の意味ではなく、ソース横断調査で版固有の完全データが見つからなかったという意味です。

## iOS 27の変更履歴

Appleの[27向け公式ノート](https://support.apple.com/en-us/149045)（2026-10-26更新）にある24アクション、既存アクションの変更、オートメーション、自然言語作成機能を反映しました。27.2のオートメーションやUse Modelの変更も含みます。ToolKitの完全なID・引数スナップショットは27.0 Simulator（2026-06-13）のままなので、27.2の項目名を内部IDや実行可能なplistスキーマとして扱いません。iOS 27.2では追加で「iPhoneを開閉」等の自動化が公式ノートに記載されています。

[26→27の比較記録](https://talk.automators.fm/t/os-26-27-new-and-updated-actions/19177)の追加アクション、廃止・改称、パラメータ差を個別行に分けました。記事の初期ベータ観測とToolKit v78（2026-06-13）のスナップショットは時点が異なります。後続ベータで識別子やUI表記が変わる可能性があるため、変更履歴はコミュニティ報告、IDと引数欄はToolKit観測として区別します。

## 生成方法とCLI

```powershell
shortcutforge actions list --os 27 --lang en --output ios27.en.md
shortcutforge actions list --os 27 --lang ja --output ios27.ja.md
shortcutforge actions list --os 26 --lang en --output ios26.en.md
shortcutforge actions list --os 26 --lang ja --output ios26.ja.md
```

iOS 27の一覧には観測済み1,206 IDと判明している引数情報を出力します。iOS 26は変更履歴・候補を出力し、未確認IDを版固有の事実として表示しません。コマンドの正確なオプションは`shortcutforge actions list --help`で確認してください。

## 検証レベル

1. JSONデータの整合性・重複ID・上流IDとの一致を検査する。
2. 公開Python APIでiOS版の絞り込み、英日Markdown、引数・enum表示を検査する。
3. テストはShortcutForgeのデータ読込と出力を検証する。
4. iPhone実機への全アクションのインポート・実行は行っていない。iOS 26/27の実機検証済みとは扱わない。

関連する手順と安全基準は[アクション互換性と検証](action-compatibility.md)を参照してください。
