# Appleショートカット アクションカタログ

アクションを選ぶ前に、対象端末にインストールされているiOSバージョンを選んでください。iOSの版によってアクションが追加・変更・削除される場合があるため、別の版で見つけたアクションが対象端末にもあるとは限りません。対象版の日本語Markdownカタログを生成します。

```sh
shortcutforge actions list --os 26 --lang ja --format markdown --output ios26-actions.ja.md
```

`17`、`18`、`27`も指定できます。英語版は`--lang en`、検索語の絞り込みは`--query calendar`を追加します。生成ファイルには版ごとの変更履歴、識別子、別名・表示名、根拠の状態、出典リンクが入ります。

`--lang ja`は見出しと整理済み変更履歴を日本語にします。アクション名はShortcutsアプリや内部識別子と照合できるよう、出典の表記（多くは英語）を保ちます。

## バージョン別の根拠

全バージョンの識別子が同じ精度で確認できているわけではありません。iOS 27はiOS 27 Simulatorで確認された識別子が1,206件あります。それ以前の版は、版を特定した完全な識別子一覧がないため、候補として表示します。下表の変更履歴は、iOS 17、iOS 26.1／26.4、iOS 27 betaで追加・変更されたと報告された名称です。すべての項目に内部識別子や完全な引数仕様があることを意味しません。

| 追加・変更時期 | 根拠の範囲 | 出典 |
|---|---|---|
| iOS 17 | iOS 16からの変更報告。時計、ファイル、カメラ、モバイル通信など | [Automators Talk](https://talk.automators.fm/t/ios-16-17-new-and-updated-actions-and-backward-incompatibility/16523) |
| iOS 26.1 | iOS 18.4からの変更報告。iOS用とMac専用の項目を含み、出典にある範囲を記載 | [Automators Talk](https://talk.automators.fm/t/ios-18-26-1-new-and-updated-actions/19029) |
| iOS 26.4 | iOS 26.2からの変更報告。OS限定の項目は注記付き | [Automators Talk](https://talk.automators.fm/t/os-26-2-26-4-new-and-updated-actions/19117) |
| iOS 27 beta | OS 26.5からbeta 4までの変更報告とiOS 27 Simulatorの識別子一覧 | [変更履歴](https://talk.automators.fm/t/os-26-27-new-and-updated-actions/19177)、[識別子データ](https://github.com/viticci/shortcuts-playground-plugin) |

識別子が一覧にあるだけでは、実機で動くことや引数仕様の正しさは保証されません。利用可否が不明なら、対象iOS版から書き出したショートカットまたは同じ版を確認できる信頼できる資料を調べてください。アクションの訂正・追加、版情報や出典、英語・日本語の修正PRを歓迎します。可能な場合は、根拠となる資料と確認したiOSバージョン・端末またはSimulatorを記載してください。
