# ACR NR GUI

Assetto Corsa Rally v0.7 の DLSS Neural Rendering をプレイ中に調整する非公式ツールです。NRのオン・オフ、全体の強度、処理回数、追加パスの強度、スタイル、トーン、細部の強調を変更できます。

## 導入

1. Windows版Assetto Corsa Rally、NRが動く環境、UE4SS、Python 3.13（Windows用ランチャーとTkinter付き）を用意します。
2. ゲームを終了し、`mod/ACRNeuralRendering` をゲームの `acr/Binaries/Win64/ue4ss/Mods` にコピーします。
3. Steamからゲームを起動し、展開したフォルダーで `ACR-NR-GUI.cmd` を開きます。

GUI下部にゲームから読み返した値が表示されます。処理回数を増やすとGPU負荷が上がります。トーン・細部・スタイルを空欄にすると、その項目の上書きを停止します。

アンインストールするにはゲームを終了し、配置した `ACRNeuralRendering` フォルダーを取り外します。

## クレジット

このMODを動画や配信で紹介する際は、概要欄などにチャンネルへのリンクを記載していただけると嬉しいです。 [Uzu Rally Lab](https://www.youtube.com/@Uzuramcrae)

コードは [MIT License](LICENSE) で公開しています。
