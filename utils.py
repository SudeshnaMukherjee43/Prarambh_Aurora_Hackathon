def recommend_careers(data, user_skills):
    def has_matching_skill(required_skills):
        # Split the string of required skills and make all lowercase
        required = [skill.strip().lower() for skill in required_skills.split(",")]
        for skill in user_skills:
            if skill.lower() in required:
                return True
        return False

    # Filter and return only those rows with at least one matching skill
    return data[data['required_skills'].apply(has_matching_skill)]
