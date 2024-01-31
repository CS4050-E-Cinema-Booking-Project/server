import React, { useEffect, useState } from "react";
import {
    Box,
    Button,
    Flex,
    Input,
    InputGroup,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalFooter,
    ModalHeader,
    ModalOverlay,
    Stack,
    Text,
    useDisclosure
} from "@chakra-ui/react";

const MoviesContext = React.createContext({
  movies: [], fetchMovies: () => {}
})

export default function Movies() {
    const [movies, setMovies] = useState([])
    const fetchMovies = async () => {
      const response = await fetch("http://localhost:8000/movie")
      const movies = await response.json()
      setMovies(movies.data)
    }
    useEffect(() => {
      fetchMovies()
    }, [])
    return (
        <MoviesContext.Provider value={{movies, fetchMovies}}>
          <AddMovie />
          <Stack spacing={5}>
            {
              movies.map((movie) => (
                <MovieHelper item={movie.item} id={movie.id} fetchMovies={fetchMovies} />
              ))
            }
          </Stack>
        </MoviesContext.Provider>
      )
  }

function AddMovie() {
    const [item, setItem] = React.useState("")
    const {movies, fetchMovies} = React.useContext(MoviesContext)
    
    const handleInput = event  => {
        setItem(event.target.value)
      }
      
      const handleSubmit = (event) => {
        const newMovie = {
          "id": movies.length + 1,
          "item": item
        }
      
        fetch("http://localhost:8000/movie", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(newMovie)
        }).then(fetchMovies)
      }

    return (
    <form onSubmit={handleSubmit}>
        <InputGroup size="md">
        <Input
            pr="4.5rem"
            type="text"
            placeholder="Add a Movie"
            aria-label="Add a Movie"
            onChange={handleInput}
        />
        </InputGroup>
    </form>
    )
}

function UpdateMovie({item, id}) {
    const {isOpen, onOpen, onClose} = useDisclosure()
    const [movie, setMovie] = useState(item)
    const {fetchMovies} = React.useContext(MoviesContext)

    const updateMovie = async () => {
        await fetch(`http://localhost:8000/movie/${id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ item: movie })
        })
        onClose()
        await fetchMovies()
      }
    
      return (
        <>
          <Button h="1.5rem" size="sm" onClick={onOpen}>Update Movie</Button>
          <Modal isOpen={isOpen} onClose={onClose}>
            <ModalOverlay/>
            <ModalContent>
              <ModalHeader>Update Movie</ModalHeader>
              <ModalCloseButton/>
              <ModalBody>
                <InputGroup size="md">
                  <Input
                    pr="4.5rem"
                    type="text"
                    placeholder="Add a Movie"
                    aria-label="Add a Movie"
                    value={movie}
                    onChange={event => setMovie(event.target.value)}
                  />
                </InputGroup>
              </ModalBody>
      
              <ModalFooter>
                <Button h="1.5rem" size="sm" onClick={updateMovie}>Update Movie</Button>
              </ModalFooter>
            </ModalContent>
          </Modal>
        </>
      )
  }

function MovieHelper({item, id, fetchMovies}) {
    return (
      <Box p={1} shadow="sm">
        <Flex justify="space-between">
          <Text mt={4} as="div">
            {item}
            <Flex align="end">
              <UpdateMovie item={item} id={id} fetchMovies={fetchMovies}/>
              <DeleteMovie id={id} fetchMovies={fetchMovies}/>  {/* new */}
            </Flex>
          </Text>
        </Flex>
      </Box>
    )
  }


function DeleteMovie({id}) {
    const {fetchMovies} = React.useContext(MoviesContext)
  
    const deleteMovie = async () => {
      await fetch(`http://localhost:8000/movie/${id}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: { "id": id }
      })
      await fetchMovies()
    }
  
    return (
      <Button h="1.5rem" size="sm" onClick={deleteMovie}>Delete Movie</Button>
    )
}