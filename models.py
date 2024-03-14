from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Date


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    image = Column(String)
    trailer = Column(String)
    director = Column(String)
    genre = Column(String)
    releaseDate = Column(String)

class UserType(Base):
    __tablename__ = 'userTypes'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userTypeName = Column(String)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    firstName = Column(String)
    lastName = Column(String)
    email = Column(String)
    phoneNumber = Column(String)
    password = Column(String)
    confirmPassword = Column(String)
    userStatus = Column(Integer)
    userType = Column(Integer)
    

class PaymentCard(Base):
    __tablename__ = 'paymentCards'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userID = Column(Integer, ForeignKey(User.id))
    cardNumber = Column(Integer)
    expirationDate = Column(Date)
    billingAddress = Column(Date)

class Cinema(Base):
    __tablename__ = 'cinemas'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    address = Column(String)

class Showroom(Base):
    __tablename__ = 'showrooms'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cinemaId = Column(Integer, ForeignKey(Cinema.id))
    capacity = Column(Integer)
    roomId = Column(Integer)

class Theater(Base):
    __tablename__ = 'theaters'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cinemaId = Column(Integer, ForeignKey(Cinema.id))
    capacity = Column(Integer)
    roomId = Column(Integer)

class Show(Base):
    __tablename__ = 'shows'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movieId = Column(Integer, ForeignKey(Movie.id))
    showroomID = Column(Integer, ForeignKey(Showroom.id))

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    showId = Column(Integer, ForeignKey(Show.id))
    userID = Column(Integer, ForeignKey(User.id))

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    TicketType = Column(String)

class BookingTicket(Base):
    __tablename__ = 'bookingsTickets'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bookingID = Column(Integer, ForeignKey(Cinema.id))
    ticketID = Column(Integer, ForeignKey(Ticket.id))

class Actor(Base):
    __tablename__ = 'actors'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    firstName = Column(String)
    lastName = Column(String)
    imdbLink = Column(String)

class MovieActor(Base):
    __tablename__ = 'moviesActors'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movieID = Column(Integer, ForeignKey(Movie.id))
    actorID = Column(Integer, ForeignKey(Actor.id))



