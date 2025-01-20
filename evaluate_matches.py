import pandas as pd
import streamlit as st

def main():
    # Load latest matches
    matches_df = pd.read_csv('./matches/nlp_business_all_matches_19_23-52.csv')
    
    st.title("Match Evaluation Dashboard")
    
    # Show match statistics
    st.write("## Match Statistics")
    st.write(f"Total matches: {len(matches_df)}")
    # st.write(f"Average confidence score: {matches_df['confidence_score'].mean():.3f}")
    
    # Match reviewer
    st.write("## Review Matches")
    for idx, match in matches_df.iterrows():
        st.write("---")
        st.write(f"### Match {idx+1}")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Buyer**")
            st.write(f"Title: {match['buyer_title']}")
            st.write(f"buyer_description: {match['buyer_description']}")
            st.write(f"buyer_nace_code: {match['buyer_nace_code']}")
            st.write(f"buyer_location: {match['buyer_location']}")
            
        with col2:
            st.write("**Seller**") 
            st.write(f"Title: {match['seller_title']}")
            st.write(f"seller_description: {match['seller_description']}")
            st.write(f"seller_nace_code: {match['seller_nace_code']}")
            st.write(f"seller_location: {match['seller_location']}")
            
        quality = st.radio(
            f"Rate match quality #{idx+1}",
            ['Good match', 'Partial match', 'Poor match'],
            key=f"quality_{idx}"
        )
        
        # Save ratings to CSV
        if st.button(f'Save rating #{idx+1}'):
            ratings_df = pd.DataFrame({
                'match_id': [idx],
                'rating': [quality],
                'buyer_title': [match['buyer_title']],
                'seller_title': [match['seller_title']]
            })
            ratings_df.to_csv('./matches/match_ratings.csv', 
                            mode='a', header=False, index=False)
            st.success(f"Rating saved for match #{idx+1}")

if __name__ == "__main__":
    main()
