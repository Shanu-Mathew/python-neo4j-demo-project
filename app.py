import streamlit as st
from neo4j import GraphDatabase


# Neo4j Configuration
neo4j_uri = 'bolt://52.54.78.34:7687'
neo4j_user = 'neo4j'
neo4j_password = 'readings-nylons-harnesses'

# Neo4j Database Connection
driver=GraphDatabase.driver(neo4j_uri,auth=(neo4j_user,neo4j_password))


# Function to get the movie details
def get_movie_details(movie_name):
    cypher_query_movie_1 = """MATCH (n:Movie) WHERE n.title = $title RETURN n as movie_info;"""
    cypher_query_movie_2 = """MATCH (m:Movie {title: $title})<-[rel:DIRECTED|WROTE|PRODUCED|REVIEWED|ACTED_IN]-(p:Person)
                            RETURN p.name as Name, type(rel) as Role;"""
    with driver.session() as session:
        movie_details = session.execute_read(
            lambda tx: tx.run(
                cypher_query_movie_1, title=movie_name
            ).data()
        )

        people_info= session.execute_read(
            lambda tx: tx.run(
                cypher_query_movie_2,title=movie_name
            ).data()
        )
    
    if movie_details is not None and people_info is not None and len(movie_details) > 0:
        results = {"movie_info": movie_details[0]["movie_info"], "people_info": people_info}
    else:
        results = None
    return results


#Function to get director details
def get_director_details(dir_name):
    cypher_query_director_1 = """MATCH (n:Person) WHERE n.name = $name RETURN n as dir_info"""
    cypher_query_director_2 = """MATCH (m:Movie)<-[:DIRECTED]-(p:Person{name:$name}) RETURN m.title as Movie"""
    with driver.session() as session:
        director_details = session.execute_read(
            lambda tx: tx.run(
                cypher_query_director_1, name=dir_name
            ).data()
        )
        director_movies = session.execute_read(
            lambda tx: tx.run(
                cypher_query_director_2,name=dir_name
            ).data()
        )
    if director_details is not None and director_movies is not None and len(director_details) > 0:
        results = {"director_info": director_details[0]["dir_info"], "director_movies": director_movies}
    else:
        results = None
    return results


#Function to get actor details
def get_actor_details(actor_name):
    cypher_query_actor_1 = """MATCH (n:Person) WHERE n.name = $name RETURN n as actor_info"""
    cypher_query_actor_2 = """MATCH (m:Movie)<-[:ACTED_IN]-(p:Person{name:$name}) RETURN m.title as Movie"""

    with driver.session() as session:
        actor_details = session.execute_read(
            lambda tx: tx.run(
                cypher_query_actor_1, name=actor_name
            ).data()
        )
        actor_mov_details = session.execute_read(
            lambda tx: tx.run(
                cypher_query_actor_2, name=actor_name
            ).data()
        )
    
    if actor_details is not None and actor_mov_details is not None and len(actor_details) > 0:
        results = {"actor_details": actor_details[0]["actor_info"], "actor_movies": actor_mov_details}
    else:
        results = None
    
    return results


#Function to print movie details
def print_movie_details(details):
    st.header(details["movie_info"]["title"])
    st.write('Tagline:- ', details["movie_info"]['tagline'])
    st.write('Release Date:- ', details["movie_info"]['released'])
    st.write(' ')

    directors = [director["Name"] for director in details["people_info"] if director["Role"] == "DIRECTED"]
    if directors:
        st.write("Directed By:")
        for director in directors:
            st.write('==> ', director)
        st.write('\n\n')

    writers = [writer["Name"] for writer in details["people_info"] if writer["Role"] == "WROTE"]
    if writers:
        st.write("Written By:")
        for writer in writers:
            st.write('==> ', writer)
        st.write('\n\n')

    producers = [producer["Name"] for producer in details["people_info"] if producer["Role"] == "PRODUCED"]
    if producers:
        st.write("Produced By:")
        for producer in producers:
            st.write('==> ', producer)
        st.write('\n\n')

    reviewers = [reviewer["Name"] for reviewer in details["people_info"] if reviewer["Role"] == "REVIEWED"]
    if reviewers:
        st.write("Reviewed By:")
        for reviewer in reviewers:
            st.write('==> ', reviewer)
        st.write('\n\n')

    actors = [actor["Name"] for actor in details["people_info"] if actor["Role"] == "ACTED_IN"]
    if actors:
        st.write("Actors:")
        for actor in actors:
            st.write('==> ', actor)
        st.write('\n\n')


#Function to print director details
def print_director_details(details):
    st.header(details["director_info"]["name"])
    st.write('Year Of Birth:- ', details["director_info"]['born'])
    st.write('\n\n')

    st.write('Movies:')
    director_movies = details.get("director_movies", [])
    for index, movie in enumerate(director_movies):
        title = movie.get("Movie", f"Movie {index + 1}")
        st.write(f"{index + 1}. {title}")


#Function to print actor details
def print_actor_details(details):
    st.header(details["actor_details"]["name"])
    st.write('Year Of Birth:- ', details["actor_details"]['born'])
    st.write('\n\n')

    st.write('Movies:')
    actor_movies = details.get("actor_movies", [])
    for index, movie in enumerate(actor_movies):
        title = movie.get("Movie", f"Movie {index + 1}")
        st.write(f"{index + 1}. {title}")


if __name__ == "__main__":
    st.title("Movie Research")
    with st.form(key='movie-form'):
        selected_type= st.selectbox("Select Type",("Movie","Director","Actor"))
        input_data = st.text_input("Movie Title")
        button= st.form_submit_button("Search",type="primary" )
    
    if button:
        if selected_type == "Movie":
            movie_details = get_movie_details(input_data)
            
            if movie_details is not None:
                print_movie_details(movie_details)
            else:
                st.header('Record Not Found')
        if selected_type == "Director":
            dir_details = get_director_details(input_data)

            if dir_details is not None:
                print_director_details(dir_details)
            else:
                st.header('Record Not Found')
            
        if selected_type == "Actor":
            actor_details = get_actor_details(input_data)

            if actor_details is not None:
                print_actor_details(actor_details)
            else:
                st.header('Record Not Found')
