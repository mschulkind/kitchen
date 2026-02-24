#!/bin/bash
# Setup LD_LIBRARY_PATH for WeasyPrint native dependencies (glib, pango, cairo, etc.)
# These are installed via nix packages in yolo-jail.jsonc but their lib dirs
# aren't automatically on the linker path.

_nix_lib_path=""
for lib in libgobject libpango libcairo libharfbuzz libfontconfig libgdk_pixbuf libfreetype libffi; do
    _found=$(ls /nix/store/*/lib/${lib}*.so 2>/dev/null | head -1)
    if [ -n "$_found" ]; then
        _dir=$(dirname "$_found")
        _nix_lib_path="${_nix_lib_path:+${_nix_lib_path}:}${_dir}"
    fi
done

if [ -n "$_nix_lib_path" ]; then
    export LD_LIBRARY_PATH="${_nix_lib_path}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
fi

# Ensure Noto Color Emoji is registered with fontconfig
_emoji_font=$(ls /nix/store/*/share/fonts/noto/NotoColorEmoji.ttf 2>/dev/null | head -1)
if [ -n "$_emoji_font" ]; then
    _xdg="${XDG_DATA_HOME:-$HOME/.local/share}"
    mkdir -p "$_xdg/fonts"
    ln -sf "$_emoji_font" "$_xdg/fonts/NotoColorEmoji.ttf" 2>/dev/null
fi

unset _nix_lib_path _found _dir _emoji_font _xdg
