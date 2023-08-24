# Create streamlit app

# To deploy on Heroku
- Create a setup.sh file
- Create a Procfile
- Deploy on Github
- Link Github repo to Heroku
- Heroku will do the rest
To get logs in terminal : heroku logs --tail --app appname

# Analytics
Source: https://github.com/jrieke/streamlit-analytics
https://jrieke-streamlit-analytics-examplessharing-demo-gllu2g.streamlit.app/?analytics=on

## Installation 
```
pip install streamlit-analytics
```

## How to use it
```
import streamlit as st
import streamlit_analytics

with streamlit_analytics.track():
    st.text_input("Write something")
    st.button("Click me")
```

or 

```
streamlit_analytics.start_tracking()
# your streamlit code here
streamlit_analytics.stop_tracking()
```

## More info
To view the results, open your app like normal and append ?analytics=on to the URL (e.g. http://localhost:8501/?analytics=on). The results are then shown directly below your app (see image above).

## Set a password
```
streamlit_analytics.track(unsafe_password="test123")
# or pass the same arg to **stop_tracking**
```

## Store analytics in a json file
### Store
```
streamlit_analytics.track(save_to_json="path/to/file.json")
# or pass the same arg to **stop_tracking**
```

### Load
```
streamlit_analytics.track(load_from_json="path/to/file.json")
# or pass the same arg to **start_tracking**
```

## Store analytics in a firebase database (google cloud)
If you don't want the results to get reset after restarting streamlit (e.g. during deployment), you can sync them to a Firestore database. Follow this blogpost to set up the database and pass the key file and collection name:

```
streamlit_analytics.track(firestore_key_file="firebase-key.json", firestore_collection_name="counts")
# or pass the same args to **start_tracking** AND **stop_tracking**
```

Note: more info to create a firestore database here: https://blog.streamlit.io/streamlit-firestore/