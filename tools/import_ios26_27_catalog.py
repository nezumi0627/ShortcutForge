from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'src/shortcutforge/data'
SNAP = DATA / 'source-snapshots/toolkit-v78'
SIM = 'iOS 27 Simulator'

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

ids_data = read(SNAP / 'ios27-tool-ids.json')
ids = set(ids_data['ids'])
tool_data = read(SNAP / 'first-party-parameter-keys.json')['tools']
enum_types = read(SNAP / 'first-party-enum-cases.json')['types']
catalog_path = DATA / 'action_catalog.json'
catalog = read(catalog_path)
assert ids == {key for key, action in catalog['actions'].items() if action.get('availability', {}).get('27') == 'observed'}

names_path = DATA / 'action_names.json'
names = read(names_path)
enriched = 0
for identifier in ids:
    tool = tool_data.get(identifier)
    if not tool or SIM not in tool.get('platforms', []):
        continue
    action = catalog['actions'][identifier]
    params = []
    for raw in tool.get('parameters', []):
        if SIM not in raw.get('platforms', []):
            continue
        item = {
            'key': raw['key'], 'name': raw.get('name'), 'type': raw.get('typePythonName'),
            'sort_order': raw.get('sortOrder'), 'flags': raw.get('flags'),
            'platforms': raw.get('platforms', []),
        }
        enum = enum_types.get(raw.get('typePythonName'))
        if enum and SIM in enum.get('platforms', []):
            item['enum_cases'] = enum.get('cases', [])
        params.append(item)
    action['parameters'] = params
    action['tool_type'] = tool.get('toolType')
    action['tool_platforms'] = tool.get('platforms', [])
    action['parameter_evidence'] = {
        'source': 'Shortcut Playground ToolKit v78 first-party parameter snapshot',
        'url': 'https://github.com/viticci/shortcuts-playground-plugin/tree/2de03bffe4ce8802e06d184931d9e4ec366a2ef2',
        'platform': SIM, 'os_version': '27', 'observed_at': '2026-06-13',
    }
    if tool.get('displayName'):
        names['names'][identifier] = tool['displayName']
    enriched += 1
write(catalog_path, catalog)
write(names_path, names)
print(f'enriched {enriched} iOS 27 tools; {len(ids)} identifiers')

# Expand exact iOS 26 release-note lists into individual bilingual records.
changes_path = DATA / 'version_changes.json'
changes_data = read(changes_path)
changes = changes_data['changes']
changes = [row for row in changes if not (row['since'] == '26.0' and row['source'] == 'ios26_apple')]
items = [
('Freeform: Add Files to Board','Freeform：ボードにファイルを追加','iOS / iPadOS / macOS'),
('Image Playground: Create Image','Image Playground：画像を作成','iOS / iPadOS / macOS'),
('Mail: Find Message','メール：メッセージを検索','iOS / iPadOS / macOS'),
('Measure: Launch Measure','計測：計測アプリを開く','iOS'),
('Messages: Find Message','メッセージ：メッセージを検索','iOS / iPadOS / macOS'),
('Messages: Find Conversation','メッセージ：会話を検索','iOS / iPadOS / macOS'),
('Screen Time: Get App & Website Data','スクリーンタイム：アプリとWebサイトのデータを取得','iOS / iPadOS / macOS'),
('Sports: Get Upcoming Sports Events','スポーツ：今後のスポーツイベントを取得','iOS / iPadOS / macOS'),
('Photos: Rename Album','写真：アルバムの名前を変更','iOS / iPadOS / macOS'),
('Photos: Search Photos','写真：写真を検索','iOS / iPadOS / macOS'),
('Photos: Create New Memory','写真：新しいメモリーを作成','iOS / iPadOS / macOS'),
('Photos: Filter Library','写真：ライブラリをフィルタ','iOS / iPadOS / macOS'),
('Reminders: Show Quick Reminder','リマインダー：クイックリマインダーを表示','iOS / iPadOS'),
('Stocks: Delete Symbol from Watchlist','株価：ウォッチリストから銘柄を削除','iOS / iPadOS / macOS'),
('Stocks: Add Symbol to Watchlist','株価：ウォッチリストに銘柄を追加','iOS / iPadOS / macOS'),
('Use Model','モデルを使用','iOS / iPadOS / macOS'),
('Visual Intelligence: Open Visual Intelligence','ビジュアルインテリジェンス：機能を開く','iOS'),
('Voice Memos: Find Voice Recording','ボイスメモ：録音を検索','iOS / iPadOS / macOS'),
('Weather: Add Location to List','天気：リストに場所を追加','iOS / iPadOS / macOS'),
('Weather: Remove Locations from List','天気：リストから場所を削除','iOS / iPadOS / macOS'),
('Writing Tools: Adjust Tone of Text','作文ツール：テキストのトーンを調整','iOS / iPadOS / macOS'),
('Writing Tools: Make List from Text','作文ツール：テキストからリストを作成','iOS / iPadOS / macOS'),
('Writing Tools: Make Table from Text','作文ツール：テキストから表を作成','iOS / iPadOS / macOS'),
('Writing Tools: Proofread Text','作文ツール：テキストを校正','iOS / iPadOS / macOS'),
('Writing Tools: Rewrite Text','作文ツール：テキストを書き直す','iOS / iPadOS / macOS'),
('Writing Tools: Summarise Text','作文ツール：テキストを要約','iOS / iPadOS / macOS'),
]
for en, ja, platform in items:
    changes.append({'since':'26.0','baseline':'iOS 18','source':'ios26_apple','name_en':en,'name_ja':ja,'change':'added','platform':platform,'platform_ja':platform.replace('iOS','iOS').replace('iPadOS','iPadOS').replace('macOS','macOS')})
# Add explicit point-release entries that were buried in grouped descriptions.
point_items = [
('26.1','26.0','Search in Files','ファイルを検索','added','iOS'),
('26.1','26.0','Photos: Open Person','写真：人物を開く','added','iOS / iPadOS / macOS'),
('26.1','26.0','Photos: Set Library View','写真：ライブラリ表示を設定','added','iOS / iPadOS / macOS'),
('26.1','26.0','Add Alarm: Open When Run parameter','アラームを追加：「実行時に開く」パラメータ','parameter','iOS / iPadOS / macOS'),
('26.1','26.0','Create List: Type parameter','リストを作成：「種類」パラメータ','parameter','iOS / iPadOS / macOS'),
('26.1','26.0','Notes: Add File renamed to Add File to Note','メモ：「ファイルを追加」から「メモにファイルを追加」に改称','name_change','iOS / iPadOS / macOS'),
('26.1','26.0','Show Result renamed to Show Content','「結果を表示」から「コンテンツを表示」に改称','name_change','iOS / iPadOS / macOS'),
('26.4','26.2','Set Battery Charge Limit','バッテリー充電上限を設定','added','iOS / iPadOS / macOS'),
('26.4','26.2','Create Reminder: Urgent priority','リマインダーを作成：「緊急」優先度','parameter','iOS / iPadOS / macOS'),
('26.4','26.2','Find Places: relevance and distance sort','場所を検索：関連度・距離順','parameter','iOS / iPadOS / macOS'),
]
for since, baseline, en, ja, kind, platform in point_items:
    changes.append({'since':since,'baseline':f'iOS {baseline}','source':'ios26_1' if since=='26.1' else 'ios26_4','name_en':en,'name_ja':ja,'change':kind,'platform':platform,'platform_ja':platform})
changes_data['changes'] = changes
write(changes_path, changes_data)
print(f'iOS 26.0 additions: {sum(x["since"] == "26.0" for x in changes)}')
