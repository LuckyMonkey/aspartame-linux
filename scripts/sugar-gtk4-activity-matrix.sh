#!/usr/bin/env bash
set -euo pipefail

if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This probe is guest-only; run it inside the Aspartame VM.' >&2
    exit 2
fi

declare -a activities=(
    'org.laptop.HelpActivity|helpactivity4.HelpActivity'
    'org.aspartame.Count|countactivity4.CountActivity'
    'org.aspartame.Calculate|calculateactivity4.CalculateActivity'
    'tv.alterna.Clock|clockactivity4.ClockActivity'
    'org.laptop.JAMClock|jamclockactivity4.JAMClockActivity'
    'org.laptop.ImageViewerActivity|ImageViewerActivity.ImageViewerActivity'
    'org.laptop.Terminal|terminal.TerminalActivity'
    'org.laptop.WebActivity|webactivity.WebActivity'
    'org.laptop.Log|logviewer.LogActivity'
    'org.laptop.Mastermind|mastermindactivity4.MastermindActivity'
    'org.worldwideworkshop.PollBuilder|pollactivity4.PollActivity'
    'mulawa.Mancala|mancalaactivity4.MancalaActivity'
    'net.coderanger.olpc.reversi|reversiactivity4.ReversiActivity'
    'mulawa.Jumble|jumbleactivity4.JumbleActivity'
    'org.sugarlabs.NumRush|numberrushactivity4.NumberRushActivity'
    'mulawa.AcrossDown|acrossdownactivity4.AcrossDownActivity'
    'mulawa.IQ|iqactivity4.IQActivity'
    'mulawa.AppelHaken|appelhakenactivity4.AppelHakenActivity'
    'org.sugarlabs.BallAndBrick|ballandbrickactivity4.BallAndBrickActivity'
    'com.jotaro.ImplodeActivity|implodeactivity4.ImplodeActivity'
    'org.laptop.PlayGo|playgoactivity4.PlayGoActivity'
    'org.laptop.BlockPartyActivity|blockpartyactivity4.BlockPartyActivity'
    'org.laptop.community.TypingTurtle|typingturtleactivity4.TypingTurtleActivity'
    'org.laptop.Memorize|memorizeactivity4.MemorizeActivity'
    'vu.lux.olpc.Maze|mazeactivity4.MazeActivity'
    'org.eq.FotoToon|fototoonactivity4.FotoToonActivity'
    'org.sugarlabs.PortfolioActivity|portfolioactivity4.PortfolioActivity'
    'org.sugarlabs.Markdown|markdownactivity4.MarkdownActivity'
    'org.laptop.community.Finance|financeactivity4.FinanceActivity'
    'org.laptop.Words|wordsactivity4.WordsActivity'
    'org.olpc-france.LOLActivity|lolactivity4.LastOneLosesActivity'
    'org.sugarlabs.GTDActivity|gtdactivity4.GTDActivity'
    'org.olpcfrance.Gridpaint|gridpaintactivity4.GridPaintActivity'
    'org.sugarlabs.StopwatchActivity|stopwatchactivity4.StopwatchActivity'
    'org.sugarlabs.GearsActivity|gearsactivity4.GearsActivity'
    'org.laptop.TurtleArtActivity|turtleartactivity4.TurtleArtActivity'
    'org.sugarlabs.gameOfLife|gameoflifeactivity4.GameOfLifeActivity'
    'org.sugarlabs.ColorMyWorldActivity|colormyworldactivity4.ColorMyWorldActivity'
    'com.homegrownapps.abacus|abacusactivity4.AbacusActivity'
    'org.sugarlabs.Planets|planetsactivity4.PlanetsActivity'
    'org.sugarlabs.Write|writeactivity4.WriteActivity'
    'org.sugarlabs.ConnectTheDots|connectthedotsactivity4.ConnectTheDotsActivity'
    'org.laptop.Pippy|pippyactivity4.PippyActivity'
    'org.sugarlabs.Paint|paintactivity4.PaintActivity'
    'com.francocorrea.diamondfusion|diamondfusionactivity4.DiamondFusionActivity'
)

script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cycles=${ACTIVITY_CYCLES:-3}

for spec in "${activities[@]}"; do
    IFS='|' read -r bundle pattern <<< "$spec"
    echo "== $bundle =="
    "$script_dir/sugar-gtk4-lifecycle-probe.sh" "$cycles" "$bundle" "$pattern"
done
echo 'activity-matrix=PASS'
