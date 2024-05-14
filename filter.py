import pandas
import datetime

pre = pandas.read_csv('pre.csv')
post = pandas.read_csv('post.csv')
i = -1

# Check if matching ID
pre_utorid, post_utorid = pre['Q14'].str.lower().str.replace(" ", ""), post['Q14'].str.lower().str.replace(" ", "")
utorids = set(pre_utorid) & set(post_utorid)

# Other filter conditions
valid_utorids = []
for utorid in utorids:
    # Check if finished survey
    pre_finished = pre.loc[pre_utorid == utorid, 'Finished'].values
    post_finished = post.loc[post_utorid == utorid, 'Finished'].values
    is_finished = len(pre_finished) > 0 and len(post_finished) > 0 and pre_finished[i] == 'True' and post_finished[i] == 'True'

    # Check if consented to data collection
    consent_msg = 'I agree to have the data I provide be analyzed as part of this study'
    pre_consent = pre.loc[pre_utorid == utorid, 'Disclosure'].values
    post_consent = post.loc[post_utorid == utorid, 'Disclosure'].values
    is_consent = len(pre_consent) > 0 and len(post_consent) > 0 and pre_consent[i] == consent_msg and post_consent[i] == consent_msg

    # Check sanity check 1
    pre_sane1 = pre.loc[pre_utorid == utorid, 'Q11_10'].values
    post_sane1 = post.loc[post_utorid == utorid, 'Q11_10'].values
    is_sane1 = len(pre_sane1) > 0 and len(post_sane1) > 0 and pre_sane1[i] == 'Extremely confident' and post_sane1[i] == 'Extremely confident'

    # Check sanity check 2
    pre_sane2 = pre.loc[pre_utorid == utorid, 'Q10_12'].values
    post_sane2 = post.loc[post_utorid == utorid, 'Q10_12'].values
    is_sane2 = len(pre_sane2) > 0 and len(post_sane2) > 0 and pre_sane2[i] == '5' and post_sane2[i] == '5'

    # Check if both surveys were done 3 hours from each other, and if pre was done before post
    pre_end_date = pre.loc[pre_utorid == utorid, 'EndDate'].values
    post_end_date = post.loc[post_utorid == utorid, 'EndDate'].values

    if len(pre_end_date) > 0 and len(post_end_date) > 0:
        pre_end_date = pandas.to_datetime(pre_end_date[i], errors='coerce')
        post_end_date = pandas.to_datetime(post_end_date[i], errors='coerce')
        is_valid_time = (post_end_date - pre_end_date).total_seconds() > 10800
    else:
        is_valid_time = False

    # Append to valid IDs
    if is_finished and is_consent and is_sane1 and is_sane2 and is_valid_time:
        valid_utorids.append(utorid)

filtered_pre = pre[pre_utorid.isin(valid_utorids)].groupby('Q14').last().sort_values(by='Q13').reset_index()
filtered_post = post[post_utorid.isin(valid_utorids)].groupby('Q14').last().sort_values(by='Q13').reset_index()

filtered_pre.to_csv('pre_filtered.csv', index=False)
filtered_post.to_csv('post_filtered.csv', index=False)
