import streamlit as st
import pandas as pd
import uuid





def main():
    st.title("Bond Portfolio Advisor")
    a=st.radio("Select Mode of Question",["Demographic Questions","Risk Assessment Questions"])
    def convert_df_to_csv(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')


    if a== 'Risk Assessment Questions':
        lst_option=[]
        lst_ans=[]
        question1 = st.radio('Which one of the following would you choose on an investment of 1000?',
                               ['a)8% returns with a 99.99% probability', 'b)12% returns with a 90% probability',
                                'c)15% return with a 80% probability'])
        lst_option.append(question1[:1])
        lst_ans.append(question1[2:])
        question2 = st.radio("2)Consider a scenario where you have made some investments in stocks, either directly or through Mutual Funds. What are you most likely to do in the event of a sudden fall in the stock market?", ['a)Pull out the money to reduce the loss','b)Pull out the money to reduce the loss','c)Invest more to leverage the falling stocks'])
        lst_option.append(question2[:1])
        lst_ans.append(question2[2:])
        question3 = st.radio("3)Are you looking for only tax free options?", ['a)Yes', 'b)No', 'c)would explore both'])
        lst_option.append(question3[:1])
        lst_ans.append(question3[2:])
        question4 = st.radio('4)In case of an emergency, would you be ready to take out your investment at a loss?', ['a)Yes','b)No', 'c)I have other options for that'])
        lst_option.append(question4[:1])
        lst_ans.append(question4[2:])
        question5 = st.radio("5)Tenor?", ['a)< 1 year','b)1-3 years','c)3-5 years','d)> 5 years'])
        lst_option.append(question5[:1])
        lst_ans.append(question5[2:])
        question6 = st.radio('6)Investment Amount', ['a)10K to 1L','b)1L to 2 L','c)2L to 5L','d)Above 5 L'])
        lst_option.append(question6[:1])
        lst_ans.append(question6[2:])
        question7 = st.radio("7)Interest Rate payment frequency", ['a)Monthly','b)Quarterly','c)Semi-Annual','d)Annual','e)Does not matter'])
        lst_option.append(question7[:1])
        lst_ans.append(question7[2:])
        if st.button("Download"):
            # if st.form_submit_button("Submit"):
            data = pd.DataFrame({"Risk Assessment Answer": lst_ans, "Risk Assessment Option": lst_option})
            #     st.dataframe(data)
            st.download_button(label="download",data=convert_df_to_csv(data),file_name='Risk Assessment.csv')
            #     submit_button = st.form_submit_button(label='Clear')
    #with st.form(key="Risk Assessment1",clear_on_submit= True):
    if a== "Demographic Questions":
            lst_option_1 = []
            lst_ans_1=[]
            qs1=st.radio("1)What is your gender?",["a)Male","b)Female"])
            lst_option_1.append(qs1[:1])
            lst_ans_1.append(qs1[2:])
            qs2 = st.radio("2)What is your current age in years?",["a)<25", "b)25 to 40", "c)40 to 50", "d)Above 50"])
            lst_option_1.append(qs2[:1])
            lst_ans_1.append(qs2[2:])
            qs3 = st.radio("3)What is your marital status?", ["a)Married","b)Single","c)Divorced"])
            lst_option_1.append(qs3[:1])
            lst_ans_1.append(qs3[2:])
            qs4 = st.radio("4)What is the highest level of education you have completed?",["a)Higher Secondary", "b)Graduation","c)PG & Above"])
            lst_option_1.append(qs4[:1])
            lst_ans_1.append(qs4[2:])
            qs5 = st.radio("5)What is your household's approximate annual gross income before taxes?",["a)< 5L", "b)5 to 10L", "c)10 to 25L", "d)25 to 50L","e)Above 50L"])
            lst_option_1.append(qs5[:1])
            lst_ans_1.append(qs5[2:])
            data_1 = pd.DataFrame({"Demographic Answer":lst_ans_1, "Demographic Option":lst_option_1})
            if st.form_submit_button("Submit"):
                data_1 = pd.DataFrame({"Demographic Answer": lst_ans_1, "Demographic Option": lst_option_1})
                data_1.append(lst_ans_1)
                st.dataframe(data_1)
                #st.download_button(label="download",data=convert_df_to_csv(data_1),file_name='Demographic.csv')
                submit_button = st.form_submit_button(label='Clear')






if __name__ == '__main__':
    main()



