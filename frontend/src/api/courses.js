import request from './index'

export function getCategories() {
  return request.get('/categories')
}

export function createCategory(data) {
  return request.post('/categories', data)
}

export function deleteCategory(id) {
  return request.delete('/categories/' + id)
}

export function getCourses(params) {
  return request.get('/courses', { params })
}

export function getCourseDetail(id) {
  return request.get('/courses/' + id)
}

export function createCourse(data) {
  return request.post('/courses', data)
}

export function updateCourse(id, data) {
  return request.put('/courses/' + id, data)
}

export function deleteCourse(id) {
  return request.delete('/courses/' + id)
}

export function createChapter(courseId, data) {
  return request.post('/courses/' + courseId + '/chapters', data)
}

export function createLesson(courseId, data) {
  return request.post('/courses/' + courseId + '/lessons', data)
}

export function updateProgress(courseId, data) {
  return request.post('/courses/' + courseId + '/progress', data)
}

export function getStudentCourses() {
  return request.get('/courses/student')
}
