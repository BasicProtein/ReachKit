param(
    [string]$Root = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

function Fail($Message) {
    Write-Error $Message
    exit 1
}

function Run-Git([string[]]$Arguments) {
    $output = & git @Arguments 2>$null
    if ($LASTEXITCODE -ne 0) {
        return $null
    }
    return $output
}

function TextFromCodepoints([int[]]$Codepoints) {
    $chars = foreach ($codepoint in $Codepoints) {
        [char]$codepoint
    }
    return -join $chars
}

$repoRoot = (Resolve-Path -LiteralPath $Root).Path
Set-Location -LiteralPath $repoRoot

$publicRoots = @("src", "tests", "examples", "README.md", "docs/README.zh-CN.md", "docs/README.ja.md", "docs/README.ko.md", "pyproject.toml")
$privateDocs = @(
    "docs/Implementation-Plan.md",
    "docs/Code-Trace-Constraint.md",
    "docs/File-Architecture.md"
)
$forbiddenPatterns = @(
    ("source " + "provenance"),
    ("reference " + "project"),
    ("target " + "project"),
    ("copy " + "from"),
    ("copied " + "from"),
    (TextFromCodepoints @(0x590D, 0x523B)),
    (TextFromCodepoints @(0x53C2, 0x8003)),
    (TextFromCodepoints @(0x7167, 0x642C)),
    (TextFromCodepoints @(0x6284, 0x88AD)),
    (TextFromCodepoints @(0x501F, 0x9274)),
    (TextFromCodepoints @(0x6765, 0x6E90)),
    (TextFromCodepoints @(0x6765, 0x6E90, 0x75D5, 0x8FF9)),
    (TextFromCodepoints @(0x53C2, 0x8003, 0x9879, 0x76EE)),
    (TextFromCodepoints @(0x4EFF, 0x7167)),
    (TextFromCodepoints @(0x642C, 0x8FD0))
)
$secretPatterns = @(
    "ghp_[A-Za-z0-9_]{20,}",
    "github_pat_[A-Za-z0-9_]{20,}",
    "xox[baprs]-[A-Za-z0-9-]{20,}",
    "sk-[A-Za-z0-9]{20,}",
    "FACEBOOK_ACCESS_TOKEN\s*=\s*['""][^'""]{20,}['""]",
    "INSTAGRAM_ACCESS_TOKEN\s*=\s*['""][^'""]{20,}['""]"
)

$files = New-Object System.Collections.Generic.List[string]
foreach ($entry in $publicRoots) {
    $path = Join-Path $repoRoot $entry
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $files.Add($path)
    } elseif (Test-Path -LiteralPath $path -PathType Container) {
        Get-ChildItem -LiteralPath $path -Recurse -File |
            Where-Object {
                $_.FullName -notmatch "\\__pycache__\\" -and
                $_.FullName -notmatch "\\.pytest_cache\\" -and
                $_.Name -ne "LICENSE"
            } |
            ForEach-Object { $files.Add($_.FullName) }
    }
}

foreach ($file in $files) {
    $text = [System.IO.File]::ReadAllText($file)
    foreach ($pattern in $forbiddenPatterns) {
        if ($text -match [regex]::Escape($pattern)) {
            Fail "Forbidden wording found in public file: $file"
        }
    }
    foreach ($pattern in $secretPatterns) {
        if ($text -match $pattern) {
            Fail "Secret-like value found in public file: $file"
        }
    }
}

$trackedPrivateDocs = Run-Git @("ls-files", "--", $privateDocs)
if ($trackedPrivateDocs) {
    Fail "Private docs are tracked by Git: $($trackedPrivateDocs -join ', ')"
}

foreach ($doc in $privateDocs) {
    if (Test-Path -LiteralPath (Join-Path $repoRoot $doc)) {
        $ignored = Run-Git @("check-ignore", "--", $doc)
        if (-not $ignored) {
            Fail "Private doc is not ignored by Git: $doc"
        }
    }
}

foreach ($pattern in $forbiddenPatterns) {
    $historyText = Run-Git @("grep", "-I", "-n", "-e", $pattern, "--", "src", "tests", "examples", "README.md", "docs/README.zh-CN.md", "docs/README.ja.md", "docs/README.ko.md")
    if ($historyText) {
        Fail "Forbidden wording found in tracked content."
    }
}

$commitMessages = Run-Git @("log", "--format=%s%n%b")
if ($commitMessages) {
    foreach ($pattern in $forbiddenPatterns) {
        if (($commitMessages -join "`n") -match [regex]::Escape($pattern)) {
            Fail "Forbidden wording found in commit messages."
        }
    }
}

$historySecrets = Run-Git @("grep", "-I", "-n", "-E", ($secretPatterns -join "|"), "--", "src", "tests", "examples", "README.md", "docs")
if ($historySecrets) {
    Fail "Secret-like value found in tracked content."
}

Write-Output "ReachKit public surface audit passed."
