# .claude ディレクトリについて

このディレクトリには、Claude Code による作業内容、計画、タスク管理などの情報が格納されています。

## ディレクトリ構成

```
.claude/
├── README.md                    # このファイル
├── implementation-plan.md       # 現在の実装計画（今後のタスク）
└── completed/                   # 完了した計画の履歴
    └── 2026-01-04-initial-implementation.md  # 初期実装の計画書
```

## ファイルの説明

### `implementation-plan.md`
現在の実装計画と今後のタスクを記載しています。
- 次に実装する機能
- 改善点
- 将来的な検討事項

### `completed/`
完了した実装の履歴を保管しています。各ファイルは実装完了時の日付でファイル名が付けられています。

## 使い方

新しいタスクや計画を追加する場合は、`implementation-plan.md` を更新してください。
大きな実装が完了した際は、その計画を `completed/` ディレクトリに移動し、新しい `implementation-plan.md` を作成してください。
