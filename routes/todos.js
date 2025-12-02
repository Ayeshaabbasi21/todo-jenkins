const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');
const {ensureAuthenticated} = require('../helpers/auth');

// load schema
require('../models/Todo');
const Todo = mongoose.model('todos');

// Todo Index Page
router.get('/', ensureAuthenticated, (req, res) => {
  Todo.find({user: req.user.id})
    .sort({creationDate: 'desc'})
    .lean()
    .then(todos => {
      res.render('todos/index', {
        todos: todos
      });
    })
    .catch(err => {
      console.error(err);
      req.flash('error_msg', 'Error loading todos');
      res.redirect('/');
    });
});

// add todo form
router.get('/add', ensureAuthenticated, (req, res) => {
  res.render('todos/add');
});

// edit todo form
router.get('/edit/:id', ensureAuthenticated, (req, res) => {
  Todo.findOne({
    _id: req.params.id
  })
  .lean()
  .then(todo => {
    if (!todo) {
      req.flash('error_msg', 'Todo not found');
      return res.redirect('/todos');
    }
    if (todo.user != req.user.id) {
      req.flash('error_msg', 'Not authorized');
      return res.redirect('/todos');
    }
    res.render('todos/edit', {
      todo: todo
    });
  })
  .catch(err => {
    console.error(err);
    req.flash('error_msg', 'Error loading todo');
    res.redirect('/todos');
  });
});

// process form - ADD TODO
router.post('/', ensureAuthenticated, (req, res) => {
  let errors = [];
 
  if (!req.body.title || req.body.title.trim() === '') {
    errors.push({text: 'Please add title'});
  }
  if (!req.body.details || req.body.details.trim() === '') {
    errors.push({text: 'Please add some details'});
  }
 
  if (errors.length > 0) {
    return res.render('todos/add', {
      errors: errors,
      title: req.body.title,
      details: req.body.details,
      dueDate: req.body.duedate
    });
  }
  
  const newTodo = {
    title: req.body.title.trim(),
    details: req.body.details.trim(),
    user: req.user.id,
    dueDate: req.body.duedate
  };
  
  new Todo(newTodo)
    .save()
    .then(todo => {
      req.flash('success_msg', 'Todo added');
      res.redirect('/todos');
    })
    .catch(err => {
      console.error(err);
      req.flash('error_msg', 'Error saving todo');
      res.redirect('/todos/add');
    });
});

// edit form process - UPDATE TODO
router.put('/:id', ensureAuthenticated, (req, res) => {
  let errors = [];
  
  if (!req.body.title || req.body.title.trim() === '') {
    errors.push({text: 'Please add title'});
  }
  if (!req.body.details || req.body.details.trim() === '') {
    errors.push({text: 'Please add some details'});
  }
  
  Todo.findOne({_id: req.params.id})
    .then(todo => {
      if (!todo) {
        req.flash('error_msg', 'Todo not found');
        return res.redirect('/todos');
      }
     
      if (todo.user != req.user.id) {
        req.flash('error_msg', 'Not authorized');
        return res.redirect('/todos');
      }
      
      if (errors.length > 0) {
        return res.render('todos/edit', {
          errors: errors,
          todo: {
            _id: req.params.id,
            title: req.body.title,
            details: req.body.details,
            dueDate: req.body.duedate
          }
        });
      }
     
      // Update values
      todo.title = req.body.title.trim();
      todo.details = req.body.details.trim();
      todo.dueDate = req.body.duedate;
     
      return todo.save();
    })
    .then(todo => {
      if (todo) {
        req.flash('success_msg', 'Todo updated');
        res.redirect('/todos');
      }
    })
    .catch(err => {
      console.error(err);
      req.flash('error_msg', 'Error updating todo');
      res.redirect('/todos');
    });
});

// delete Todo
router.delete('/:id', ensureAuthenticated, (req, res) => {
  Todo.deleteOne({
    _id: req.params.id,
    user: req.user.id
  })
  .then((result) => {
    if (result.deletedCount === 0) {
      req.flash('error_msg', 'Todo not found or not authorized');
    } else {
      req.flash('success_msg', 'Todo removed');
    }
    res.redirect('/todos');
  })
  .catch(err => {
    console.error(err);
    req.flash('error_msg', 'Error deleting todo');
    res.redirect('/todos');
  });
});

module.exports = router;
