mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
[theme]\n\
base = \"dark\"\n\
\n\
[ui]\n\
favicon = \"https://sotisimmo.s3.eu-north-1.amazonaws.com/Sotis_AI_contrast.ico\"\n\
headHtml = \"<title>Sotis Immo.</title>\"\n\
" > ~/.streamlit/config.toml
